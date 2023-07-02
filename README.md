# Telegram Bot sync with Google Calendar
A telegram bot designed to help adding of events easily from the Telegram app into Google Calendar.

## Note
Token from Telegram bot is not included and currently is an empty string.


Packages to add in terminal:


`$ pip install pyTelegramBotAPI`


`$ pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`

Setting up of Google Calendar can be found from GoogleDevelopers [here](https://developers.google.com/calendar/api/quickstart/python).

## Commands
There are 5 main commands in the current version.

### `start`

User will be greeted by welcome message and prompted to input `/menu` command.

### `menu`

Bot provides a list of commands for the user and their respective descriptions.

### `add`

User will be asked to key in a song title which will be the main title for the event created in Google Calendar

The user will then type in the events that will be added into Google Calendar in the following format:

```
Date: DD/MM
Time: HH.MMam/pm - HH.MMam/pm
CMI:
Agenda:
```

### `eg`

Bot provides an example of how the format of the events are. 

Example of Usage:

Input:

`/eg`

Expected Output:

```
Date: 01/02
Time: 9.00am - 10.30pm
CMI: IU :/ she'll come after 8pm (hopefully)
Agenda: Clean till chorus

Date: 02/02
Time: 10.00am - 12.00pm
CMI: Full crew
Agenda: Filming at MBS
```

### `delete`

User will be asked to choose a song title to be deleted from Google Calendar. 

User will then be given a list of dates and times that are under the song title and will then choose a number to delete.

Example of Usage:

Input:

`/delete`

Expected Output:

`Which song title you want to delete from?`

---
*Created by: @darrenlsx and Yukesh*