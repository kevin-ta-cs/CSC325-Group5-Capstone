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


# Architecture 

## This is the AI-generated FIGMA designed layout that we will use for our website. This is a (type) of website in which (describe the type [server/client, layered, etc.] to describe the plan.)

# Test Plan 
- Unit Testing
- Unit testing will focus on testing individual functions and components of the application to make sure they work correctly on their own.
Examples:
• Verify that users cannot submit lost or found item reports without filling in required fields.
• Test that search filters correctly identify items based on category, color, or location.
• Verify that item statuses can be updated correctly.
• Check that users receive appropriate error messages when entering invalid information.
- Integration Testing
- Integration testing will ensure that different parts of the application work correctly together, especially when communicating with the database.
Examples:
• Verify that submitting a lost or found item report successfully saves the information in the database.
• Test that newly submitted reports appear in search results and on the user's dashboard.
• Verify that editing or deleting a report correctly updates the database and displayed information.
• Test that the Al matching feature can retrieve lost and found reports and return possible matches.
• Verify that approved claims correctly update the item's status.

- System Testing
- System testing will focus on testing the entire application from the user's perspective to make sure all major features work together as expected.
Examples:
• Test the complete process of creating an account, logging in, and submitting a lost-item report.
• Verify that a user can search for a missing item, view possible matches, and submit a claim request.
• Test that an administrator can review a claim and update the item's status to returned.
• Verify that unauthorized users cannot edit or delete reports belonging to other users.
• Check that the application works properly on different screen sizes and browsers.
- Testing Goal
The overall goal of our testing plan is to ensure that the Campus Lost & Found system is reliable, easy to use, and secure. By performing unit, integration, and system testing, we aim to identify and fix problems before the application is completed.
