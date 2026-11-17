# CSC325-Group5-Capstone
Capstone project for CSC325

## Team Members
- Kevin Trejo Aleman
- Bryan Morel
- Desteny Blair
- Michael Fernandez
- Alexander Ciamillo


## Campus Lost & Found
  Bio: A  lost and found system where students, faculty, and staff can report lost or found items and search for possible matches


# Prototype Link
https://www.figma.com/make/In6Vtbg64vXmH21s9Ew4pK/FindIt-Website?t=Y2URXDZFGEdrHsjn-1

# Architecture 
"FindIt" follows a client-server architecture, separating the application into three main components:

Frontend (Client): The user interface where students can report lost or found items, search listings, and submit claims. The website prototype was designed using Figma.

Backend (Server): Handles user requests, processes item reports, manages searches, and verifies claims. It connects the frontend to the database.

Database: Stores user information, item descriptions, locations, and claim requests so information can be accessed and updated.

How It Works:

When a student interacts with the website, the frontend sends a request to the backend. The backend processes the request, retrieves or updates information in the database, and sends the results back to the frontend.

This structure keeps "FindIt" organized, easy to maintain, and expandable as new features are added.

# Test Plan 
- Unit Testing: will focus on testing individual functions and components of the application to make sure they work correctly on their own.
Examples:
• Verify that users cannot submit lost or found item reports without filling in required fields.
• Test that search filters correctly identify items based on category, color, or location.
• Verify that item statuses can be updated correctly.
• Check that users receive appropriate error messages when entering invalid information.
- Integration Testing: will ensure that different parts of the application work correctly together, especially when communicating with the database.
Examples:
• Verify that submitting a lost or found item report successfully saves the information in the database.
• Test that newly submitted reports appear in search results and on the user's dashboard.
• Verify that editing or deleting a report correctly updates the database and displayed information.
• Test that the Al matching feature can retrieve lost and found reports and return possible matches.
• Verify that approved claims correctly update the item's status.

- System Testing: will focus on testing the entire application from the user's perspective to make sure all major features work together as expected.
Examples:
• Test the complete process of creating an account, logging in, and submitting a lost-item report.
• Verify that a user can search for a missing item, view possible matches, and submit a claim request.
• Test that an administrator can review a claim and update the item's status to returned.
• Verify that unauthorized users cannot edit or delete reports belonging to other users.
• Check that the application works properly on different screen sizes and browsers.

- Testing Goal: the overall goal of our testing plan is to ensure that the Campus Lost & Found system is reliable, easy to use, and secure. By performing unit, integration, and system testing, we aim to identify and fix problems before the application is completed.

## Python-Generated Web Pages

The Django views generate the browser pages from Python source. The project does
not use separate HTML template files.

Signed-in members can toggle between lost-item and found-item reports. Each
report includes a required category, campus building, and date, with labels
reflecting whether the item was lost or found. Found-item reports also collect
a time. Both types support a specific-area detail. Buildings are selected from
the existing campus building list. Submitted reports are saved and displayed
in the campus catalog; the category choices match the catalog filters. The
home page shows up to six randomly selected reports, while Browse items opens
the searchable and filterable catalog in pages of 25 reports. Members can edit
or delete their own reports from the user dashboard.

The report form follows the prototype's in-place lost/found toggle. Found
reports may include an ownership-verification question; claimants can answer it
in a private request. Selecting a catalog item opens its detail page with its
category, description, building, date, and (for found reports) time. Signed-in
users can send private information requests for saved reports; requests appear
only in the reporter's dashboard. Static sample listings are viewable but do
not have a reporter to receive requests.

Found-item reports may include an image. Uploaded images remain private to the
reporter and report administrators until a user with `change_founditem`
permission approves them from the dashboard or Django admin. Only approved
images appear in public listings and detail pages. By default, local
development stores files under `DjangoLostandFound/media/`, which is excluded
from Git. For shared or deployed use, configure an S3-compatible object-storage
bucket as described below so every application instance can access the same
uploads.

# Running the Project

## Prerequisites
- Python 3.13 or a version compatible with the project's dependencies
- Git
- Access to the team's MongoDB database

## Installation and Setup

1. Clone the repository and open it in VS Code.
2. Open a terminal in the project directory.
3. Install the required dependencies:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

   On Windows, use `py` if the Python launcher is installed, or `python` otherwise. If neither command works, install Python and enable **Add python.exe to PATH** in the installer, then restart VS Code.

4. Create a `.env` file inside the outer `DjangoLostandFound` folder, alongside `manage.py`.

5. Add the following environment variables:

   ```dotenv
   DJANGO_SECRET_KEY=Y3VujzyOVsIuL30v4W5yuYj4kAFYeMIPubH3gJPXMDsRwcaK1LgAy2all6zpG4jF86A
   MONGODB_URI=mongodb+srv://user:password@lostandfound.db1lsrs.mongodb.net/
   ```

6. Replace the placeholders with your own authorized credentials. Never commit or share the `.env` file.

   For shared uploads, also configure an S3-compatible bucket and add its
   settings to the deployment environment (or the `.env` file for local
   testing):

   ```dotenv
   AWS_STORAGE_BUCKET_NAME=your-private-bucket
   AWS_S3_REGION_NAME=your-bucket-region
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   ```

   Use credentials with access only to that bucket. On AWS, an instance role
   can provide credentials instead of access-key environment variables. For
   S3-compatible providers, set `AWS_S3_ENDPOINT_URL` to the provider's
   endpoint. Keep the bucket private; the application serves images through
   its existing permission-checked image route. If
   `AWS_STORAGE_BUCKET_NAME` is not set, uploads remain local and are not
   shared between machines or deployments. Previously uploaded local files
   are not copied automatically; copy them to the bucket using their existing
   storage paths before switching to shared storage.

7. Navigate to the Django application directory:

   ```bash
   cd DjangoLostandFound
   ```

8. Start the development server:

   ```bash
   python3 manage.py runserver
   ```

   On Windows, run `py manage.py runserver` or `python manage.py runserver`, depending on which command works on your installation.

## Running Automated Tests

From the `DjangoLostandFound` directory, run:

```bash
python3 manage.py test myapp --noinput
```

The tests require access to a working MongoDB instance.
For repeated runs, add `--keepdb` to reuse the isolated test database:

```bash
python3 manage.py test myapp --noinput --keepdb
```

The Deploy stage does not currently publish the application to a live hosting service.

## AI Usage

The team should document any AI tools used during development, including how generated suggestions were reviewed, tested, and corrected before being included in the project.
