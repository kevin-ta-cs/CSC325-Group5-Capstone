import mimetypes

from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from .forms import DashboardUsernameForm, FoundItemForm, FoundItemInquiryForm, SignUpForm
from .models import FoundItem, FoundItemInquiry
from .pages import (
    REPORTS,
    browse_items_page,
    found_item_page,
    found_item_detail_page,
    home_page,
    login_page,
    signup_page,
    user_dashboard_page,
)


def home(request):
    return HttpResponse(home_page(request))


def browse_items(request):
    return HttpResponse(browse_items_page(request))


class PythonLoginView(LoginView):
    def render_to_response(self, context, **response_kwargs):
        return HttpResponse(
            login_page(self.request, context["form"], context.get("next", ""))
        )


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False
            user.is_superuser = False
            user.save()
            form.save_m2m()
            return redirect('login')
    else:
        form = SignUpForm()

    return HttpResponse(signup_page(request, form))


@login_required(login_url='login')
def user_dashboard(request):
    form = DashboardUsernameForm(
        request.POST if request.method == 'POST' else None,
        instance=request.user,
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Your username was updated.')
            return redirect('user_dashboard')

    can_manage_reports = (
        request.user.has_perm('myapp.change_founditem')
        or request.user.has_perm('myapp.delete_founditem')
    )
    can_approve_images = request.user.has_perm('myapp.change_founditem')
    own_items = list(request.user.found_items.order_by(
        '-date_found',
        '-time_found',
        '-created_at',
    ))
    found_items = list(
        FoundItem.objects.all().order_by(
            '-date_found',
            '-time_found',
            '-created_at',
        )
    ) if can_manage_reports else own_items
    inquiries = FoundItemInquiry.objects.filter(
        item_id__in=[item.pk for item in own_items],
    ).order_by('-created_at')
    return HttpResponse(
        user_dashboard_page(
            request,
            form,
            found_items,
            inquiries,
            can_manage_reports=can_manage_reports,
            can_approve_images=can_approve_images,
        )
    )


@login_required(login_url='login')
def report_found_item(request):
    form = FoundItemForm(
        request.POST if request.method == 'POST' else None,
        request.FILES if request.method == 'POST' else None,
    )
    if request.method == 'POST' and form.is_valid():
        found_item = form.save(commit=False)
        found_item.reporter = request.user
        found_item.save()
        messages.success(
            request,
            'Your found item was reported.'
            + (
                ' Its image will appear after admin approval.'
                if found_item.image
                else ''
            ),
        )
        return redirect('found_report')

    return HttpResponse(found_item_page(request, form))


def _found_item_or_404(item_id):
    if len(item_id) != 24 or any(
        character not in '0123456789abcdefABCDEF'
        for character in item_id
    ):
        raise Http404
    return get_object_or_404(FoundItem, pk=item_id)


def found_item_image(request, item_id):
    item = _found_item_or_404(item_id)
    if not item.image:
        raise Http404
    if not item.image_approved and not (
        request.user.is_authenticated
        and (
            item.reporter_id == request.user.pk
            or request.user.has_perm('myapp.change_founditem')
        )
    ):
        raise Http404
    response = FileResponse(
        item.image.open('rb'),
        content_type=(
            mimetypes.guess_type(item.image.name)[0]
            or 'application/octet-stream'
        ),
    )
    response['X-Content-Type-Options'] = 'nosniff'
    return response


@login_required(login_url='login')
@require_POST
def approve_found_item_image(request, item_id):
    if not request.user.has_perm('myapp.change_founditem'):
        raise PermissionDenied
    item = _found_item_or_404(item_id)
    if not item.image:
        messages.error(request, 'This report has no image to approve.')
    else:
        item.image_approved = True
        item.save(update_fields=['image_approved'])
        messages.success(request, 'The report image is now visible publicly.')
    return redirect('user_dashboard')


def found_item_detail(request, item_id):
    if item_id.startswith('sample-'):
        index_text = item_id.removeprefix('sample-')
        if not index_text.isdigit():
            raise Http404
        index = int(index_text)
        if index >= len(REPORTS):
            raise Http404
        item = REPORTS[index]
        request_status = 'unavailable'
        form = None
    else:
        item = _found_item_or_404(item_id)
        if not request.user.is_authenticated:
            request_status = 'login'
            form = None
        elif item.reporter_id == request.user.pk:
            request_status = 'own'
            form = None
        else:
            request_status = 'available'
            form = FoundItemInquiryForm()
    return HttpResponse(
        found_item_detail_page(request, item, form, request_status)
    )


@login_required(login_url='login')
@require_POST
def request_found_item_information(request, item_id):
    found_item = _found_item_or_404(item_id)
    if found_item.reporter_id == request.user.pk:
        messages.error(request, 'You cannot request information about your own report.')
        return redirect('found_item_detail', item_id=found_item.pk)

    submission_id = request.POST.get('submission_id', '')
    processed_submissions = request.session.get(
        'private_request_submission_ids',
        [],
    )
    submission_key = f'{found_item.pk}:{submission_id}'
    if submission_id and submission_key in processed_submissions:
        return redirect('found_item_detail', item_id=found_item.pk)

    form = FoundItemInquiryForm(request.POST)
    if form.is_valid():
        inquiry = form.save(commit=False)
        inquiry.item = found_item
        inquiry.requester = request.user
        inquiry.save()
        if submission_id:
            request.session['private_request_submission_ids'] = (
                processed_submissions + [submission_key]
            )[-50:]
        messages.success(request, 'Your private request was sent to the reporter.')
        return redirect('found_item_detail', item_id=found_item.pk)

    return HttpResponse(
        found_item_detail_page(
            request,
            found_item,
            form,
            request_status='available',
        )
    )


@login_required(login_url='login')
def edit_found_item(request, item_id):
    if request.user.has_perm('myapp.change_founditem'):
        found_item = get_object_or_404(FoundItem, pk=item_id)
    else:
        found_item = get_object_or_404(
            FoundItem,
            pk=item_id,
            reporter=request.user,
        )
    form = FoundItemForm(
        request.POST if request.method == 'POST' else None,
        request.FILES if request.method == 'POST' else None,
        instance=found_item,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(
            request,
            'Your found item report was updated.'
            + (
                ' Its new image is pending admin approval.'
                if request.FILES.get('image')
                else ''
            ),
        )
        return redirect('user_dashboard')

    return HttpResponse(found_item_page(request, form, editing=True))


@login_required(login_url='login')
@require_POST
def delete_found_item(request, item_id):
    if request.user.has_perm('myapp.delete_founditem'):
        found_item = get_object_or_404(FoundItem, pk=item_id)
    else:
        found_item = get_object_or_404(FoundItem, pk=item_id, reporter=request.user)
    found_item.delete()
    messages.success(request, 'Your found item report was deleted.')
    return redirect('user_dashboard')