module Main exposing (main)

import Browser
import Html exposing (..)
import Html.Attributes as Attributes
import Html.Events exposing (onInput, onSubmit)
import Http


type alias Model =
    { searchResult : String
    }


init : () -> ( Model, Cmd Msg )
init () =
    ( { searchResult = "" }
    , Http.get
        { url = "/search/", expect = Http.expectString GotLinks }
    )


type Msg
    = GotLinks (Result Http.Error String)


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        GotLinks (Ok res) ->
            ( { model | searchResult = res }, Cmd.none )

        GotLinks (Err e) ->
            let
                _ =
                    Debug.log "e" e
            in
            ( model, Cmd.none )


view : Model -> Html Msg
view model =
    div []
        [ h1 [] [ text "Here is what the route \"/search/\" responds" ]
        , text model.searchResult
        ]


main : Program () Model Msg
main =
    Browser.element
        { init = init
        , view = view
        , update = update
        , subscriptions = always Sub.none
        }

