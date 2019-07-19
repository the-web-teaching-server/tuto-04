# Tutorial 04 - AJAX calls with Elm

In the previous tutorial, you have built an url shortener.
However, the use is not what a modern web user expects: we
are redirected to a new page for each performed action.

In this tutorial, you will build your first "SPA" (Single
Page Application): the user loads a page once and all the
subsequent actions are performed in this page thanks to
Javascript (which is compiled from Elm).

Hence, the two main goals of this tutorial are:
* learn how to build a server responding only data
  (in JSON) instead of HTML,
* learn how to request a server from Elm, which includes
  how to transform JSON into Elm values.
  
## Server part
1. Look at the `server.py` file. You might be familiar with it
   since it is almost the same file from the previous tutorial:
   most of the responses has been modified to return JSON
   instead of HTML (Note however that the `/new-shortcut/`
   handler now expects Json -- `request.json['url']` -- instead
   of form-encoded data -- `request.form['url']`).
   
   Browse to the route `/view-shortcut/aoM4apKh`, you should see
   a JSON response. Look at the "Raw data" ("Données brutes" in french)
   to see exactly what the server has returned.
1. Edit the `/search/` route to return JSON instead of HTML.
1. That's it! Browse to `/search/`, you should see the search result 
   in JSON.

## Client part 

### Structure
1. Look at `front/Mail.elm`. The `init` performs a "command"
   with 
   ```elm
   Http.get { url = "/search/", expected = Http.expectString GotLinks }
   ```
   It tells to the Elm runtime:
   * request the url `/search/`
   * when you get an answer:
       - interpret it as text (the `Http.expectString` part)
       - produce a `GotLinks` message. This message will be catched by 
         the update function.
1. This following piece of code deals with error during the HTTP request:
   ```elm
           GotLinks (Err e) ->
            let
                _ =
                    Debug.log "e" e
            in
            ( model, Cmd.none )
   ```
   Currently, it should not be reached, unless there is network issue.
   * Replace the command in the init by (note the faulty url):
     ```elm
     Http.get { url = "/searc/", expected = Http.expectString GotLinks }
     ```
   * Then browse to `/`, and open the Javascript console (F12 > Console).
     You should see something like:
     ```
     e: BadStatus 404
     ```
   
1. This Elm file is compiled to the Javascript file `static/elm.js`
   (you do not have to worry too much about the content of this file). 
   The bash command performing
   this compilation is in `sh/start.sh`, the precise command is:
   ```sh
   elm make front/Main.elm --output static/elm.js
   ```
1. Then, this Javascript file is included in `templates/index.html`
   with the tag `<script src="static/elm.js">`.
   The `<div id="elm">` node will be totally controlled by
   the Elm application.

### Development process
It is possible to develop in Elm with the Glitch editor, but
this is not very convinient: syntax higlighting is not great,
the compilation errors are displayed in the logs, which are not
really readable... You can type all your code in Ellie,
and when it compiles, just copy paste all the content 
in the `src/Main.elm` file in Glitch.


Here is [the starting point for this tutorial in Ellie](https://ellie-app.com/67R92pnQ2Qna1)
 (`Ctrl + click` to open in new tab).

### Convert JSON to Elm values
   
1. Install the `elm/json` package:
   * In glitch, open the console "Tools > Logs > Console" or "Tools > Full page console" then enter:
     `elm install elm/json`.
   * In Ellie, click on the box on the left of the editor and search for "json", then click on "install".
1. Import the JSON decoder library with:
   ```elm
   import Json.Decode as Decode exposing (Decoder)
   ```
1. Create the following type alias:
   ```elm
   type alias Shortcut =
      { destinationUrl : String
      , shortLink : String
      }
   ```
   and the decoder:
   ```elm
   shortcutDecoder : Decoder Shortcut
   ```
   which will decode JSON of the shape:
   ```json
   { "url": "http://www.example.com",
     "key": "jaOk5",
     "shortcut": "http://app-name.glitch.me/r/ja0k5"
   }
   ```
   We do not really care about the `key` field, you can ignore it.
   See the lecture's slides for building the decoder.
1. Create the decoder:
   ```elm
   fromServerSearchDecoder : Decoder (List Shortcut)
   ```
   which will decode JSON of the shape (it should be the output of
   the route `/search/`):
   ```json
   {
      "matches": [
        {
          "key": "EbA356Ak",
          "shortcut": "http://toi.glitch.me/r/EbA356Ak",
          "url": "http://www.example.com"
        },
        {
          "key": "aoM4apKh",
          "shortcut": "http://toi.glitch.me/r/aoM4apKh",
          "url": "http://www.mozilla.org"
        }
      ],
      "query": ""
    }
    ```
    You can ignore the `query` field.
1. Create a function:
   ```elm
   showShortcut : Shortcut -> String
   ```
   which will transform a shortcut into a string like:
   `http://app-name.glitch.me/r/aoM4apKh ---> http://www.mozilla.org`
1. Edit:
   * the type of `Model` to be:
     ```elm
     type alias Model = { searchResult : List Shortcut }
     ```
   * the `GotLinks` message to be:
     ```elm
     type Msg
         = GotLinks (Result Http.Error (List Shortcut)
     ```
   * the command in the init to be:
     ```elm
     Http.get { url = "/search/", expected = Http.expectJson GotLinks fromServerSearchDecoder }
     ```
   Try to compile and correct all the things needed to display the links in a `ul` list (you
   may need to write auxilliary function like `viewShortcutInLi : Shortcut -> Html Msg` and
   use `List.map`).
   
   When the code compile, if the app does not display anything, check the javascript
   console (F12 > Console) to see error messages.
1. We will add a "search bar" but unlike the previous tutorial, the results will be
   updated each time the user hit the keyboard, instead of waiting a submission.
   * Add a variant `QueryUpdated String` in the `Msg` type,
   * add an input field raising this message with `onInput`,
   * edit the `update` function: when a `QueryUpdated query` message
     is catched, perform a `Http.get` command (remember that we can
     use urls like `/search/?q=example` to search for urls containing "example").
   The user should then be able to perform search!

### Add a new link

In this part, we will add a form to send new urls to the server.

1. Add a field `linkToShorten : String` in the model. It will reflect
   what the user enter in the field.
1. Take inspiration from [the todo list form](https://github.com/the-web-teaching-server/tuto-02/#add-tasks-in-the-todo-list)
   (`Ctrl+click` to open in a new tab) to build a similar form here.
1. Use the [documentation of `Json.Encode`](https://package.elm-lang.org/packages/elm/json/latest/Json-Encode#object) 
   (`Ctrl+click` to open in a new tab) to  write a function:
   `urlToValue: String -> Value` which transform an url into a `Value` (Elm representation
   for Json object) suitable for querying the server. For instance, 
   `urlToValue "http://foo.com"` should be `{ "url": "http://foo.com" }`.
1. Create three messages:
   * one triggered each time a user hits a key,
   * one triggered when the form is submitted,
   * `GotNewShortcut` triggered when the server send back the created shortcut.
     This one should looks similar to the existing
     ```elm
     GotLinks : Result Http.Error (List Shortcut) -> Msg
     ```
     but the payload should be `Shortcut` instead of `List Shortcut`.
1. Edit the `update` function to take care of the previous events.
   * For the submission,
     you should use [Http.post](https://package.elm-lang.org/packages/elm/http/latest/Http#post)
     (`Ctrl+click` to open in new tab),
     [Http.jsonBody](https://package.elm-lang.org/packages/elm/http/latest/Http#jsonBody),
     and the `urlToValue` function (previously written).

     You should also reinitialise `linkToShorten` to the empty string.
   * Ignore the payload of `GotNewShortcut` for the moment (with
     `GotNewShortcut _ -> ( model, Cmd.none )`).
     
You should have a working application. Test it by adding an URL and then searching
it.

### Optional part: more safety with the types!

We would like to give an immediate feedback to the user when he enters an url.
Hence we will display the last shortcut created under the form used to send the url.

At the begining of the app, there is not any "last shortcut", then we will represent
this state as `Nothing`. Thus we will store this information in a field 
`lastShortcut : Maybe Shortcut`.

1. Add this field to the model, and edit the `init`.
1. Deal with the `GotNewShortcut (Ok shortcut)` and `GotNewShortcut (Err e)`
   in a similar fashion as the `GotLinks` messages.
1. Edit your `view` function to display this data. You may
   need to use pattern matching on `model.lastShortcut`:
   ```elm
   case model.lastShortcut of
       Nothing ->
          ...
      
      Just shortcut ->
          ...
   ```
1. Currently, we are silently ignoring the errors in the case
   `GotNewShortcut (Err e)`, which is not user friendly.
   Hence, we will create a type to capture all those possible
   states: 
   * the application has just started, there is no "last shortcut"
     ("init" state),
   * the server correctly sent back a shortcut,
   * an error occured during the network process.
   Create the following type and change the type
   of `model.lastShortcut` to `LastShortcut`:
   ```elm
   type LastShortcut
       = ShortcutInit
       | ShortcutError
       | ShortcutReceived Shortcut
   ```
   Perform all the modifications needed to
   make the code compile. It could be a good
   idea to create a `viewLastShortcut : LastShortcut -> Html Msg`
   function.
1. Perform a similar modification of the field `searchResult` to
   deal with the errors (you should create a new type!).

This final steps of this part are very important: the types in Elm
are a very convinient and powerful way to accurately represent the
possible states of our application. You can [watch this talk](https://www.youtube.com/watch?v=IcgmSRJHu_8)
or [read this article](https://medium.com/elm-shorts/how-to-make-impossible-states-impossible-c12a07e907b5)
for further information.


     


     