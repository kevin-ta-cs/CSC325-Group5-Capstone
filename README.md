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

4. Create a `.env` file inside the outer `DjangoLostandFound` folder, alongside `manage.py`.

5. Add the following environment variables:

   ```dotenv
   DJANGO_SECRET_KEY=Y3VujzyOVsIuL30v4W5yuYj4kAFYeMIPubH3gJPXMDsRwcaK1LgAy2all6zpG4jF86A
   MONGODB_URI=MONGODB_URI=mongodb+srv://user:password@lostandfound.db1lsrs.mongodb.net/
   ```

6. Replace the placeholders with your own authorized credentials. Never commit or share the `.env` file.

7. Navigate to the Django application directory:

   ```bash
   cd DjangoLostandFound
   ```

8. Start the development server:

   ```bash
   python3 manage.py runserver
   ```

## Running Automated Tests

From the `DjangoLostandFound` directory, run:

```bash
python3 manage.py test myapp --noinput
```

The tests require access to a working MongoDB instance.

## CI/CD Pipeline

The project uses GitHub Actions to automate continuous integration and deployment preparation.

The workflow is located at:

`.github/workflows/csc325_ci_cd.yml`

It runs automatically on pushes and pull requests targeting the `main` branch.

The pipeline contains four stages:

1. **Setup:** Checks out the repository and configures Python.
2. **Dependencies:** Installs the project's required Python packages.
3. **Test:** Runs automated Django tests using a temporary MongoDB service.
4. **Deploy:** Prepares and uploads a downloadable application package after successful tests on pushes to `main`.

The Deploy stage does not currently publish the application to a live hosting service.

## GitHub Secrets

The CI/CD workflow uses the `DJANGO_SECRET_KEY` repository secret.

Authorized repository maintainers can configure it under:

**Settings → Secrets and variables → Actions**

Secret values must never be included in source code, workflow files, or Git commits.

## Contributing

1. Create a feature branch for your assigned task.
2. Implement your changes and add appropriate automated tests.
3. Commit and push your feature branch.
4. Open a pull request targeting `main` and link the relevant Kanban issue.
5. Confirm that the GitHub Actions checks pass.
6. Request at least one teammate review and approval.
7. Merge only after the required checks and approval are complete.

Direct pushes to `main` should be prevented through GitHub branch protection.

## AI Usage

The team should document any AI tools used during development, including how generated suggestions were reviewed, tested, and corrected before being included in the project.