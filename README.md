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
