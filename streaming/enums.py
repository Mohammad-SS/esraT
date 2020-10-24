def getErrors(errorNumber):
    err = {
        # User Exists Errors
        430: "Username Exist",
        431: "Phone Number Exists",
        432: "Number Id exists",
        # Login's Error
        630: "Username Doesnt Exist",
        631: "Password Doesnt Match",
        632: "User is Banned",
        400: "defective data received",
        405: "Already Loggedin",
        # conductor errors :
        607: "items are corrupted" ,
        608: "Number of items couldn't update ",
        609: "No Delete occurred",
        610: " Number of deletes Failed ",
        # live errors :
        701: "File Not Found" ,
        # Admin's Error :
        666: "User is not admin",

    }
    return err.get(errorNumber)


def getDescription(errorNumber):
    err = {
        # SignUp's Errors :
        430: "Trying to add user with same username to Users database",
        431: "Trying to add user with same Phone Number to Users database",
        432: "Trying to add user with same Number Id to Users database",
        # Login's Error's :
        630: "Trying To login with wrong username",
        631: "Trying To login with wrong password",
        632: "Trying To login with banned user",
        400: "defective data received",
        405: "Trying to Login , But SESSION[LOGEDIN] is TRUE",

        # conductor errors
        }
    return err.get(errorNumber)
