//Environment Configuration

var config = {};
config.IOT_BROKER_ENDPOINT      = "a1ii3qlfr1qukw-ats.iot.us-east-1.amazonaws.com";
config.IOT_BROKER_REGION        = "us-east-1";
config.IOT_THING_NAME           = "iot295b_thing";
config.params                   = { thingName: 'iot295b_thing' };
//Loading AWS SDK libraries

var AWS = require('aws-sdk');
AWS.config.region = config.IOT_BROKER_REGION;

//Initializing client for IoT
var iotData = new AWS.IotData({endpoint: config.IOT_BROKER_ENDPOINT});

// Route the incoming request based on type (LaunchRequest, IntentRequest,
// etc.) The JSON body of the request is provided in the event parameter.
exports.handler = function (event, context) {
    try {
        console.log("event.session.application.applicationId=" + event.session.application.applicationId);

        if (event.session.application.applicationId !== "amzn1.ask.skill.b3670fd9-4afd-4557-932b-82346132bb5d") {
             context.fail("Invalid Application ID");
        }

        if (event.session.new) {
            onSessionStarted({requestId: event.request.requestId}, event.session);
        }

        if (event.request.type === "LaunchRequest") {
            onLaunch(event.request,
                event.session,
                function callback(sessionAttributes, speechletResponse) {
                    context.succeed(buildResponse(sessionAttributes, speechletResponse));
                });
        } else if (event.request.type === "IntentRequest") {
            onIntent(event.request,
                event.session,
                function callback(sessionAttributes, speechletResponse) {
                    context.succeed(buildResponse(sessionAttributes, speechletResponse));
                });
        } else if (event.request.type === "SessionEndedRequest") {
            onSessionEnded(event.request, event.session);
            context.succeed();
        }
    } catch (e) {
        context.fail("Exception: " + e);
    }
};

/**
 * Called when the session starts.
 */
function onSessionStarted(sessionStartedRequest, session) {
    console.log("onSessionStarted requestId=" + sessionStartedRequest.requestId +", sessionId=" + session.sessionId);
}

/**
 * Called when the user launches the skill without specifying what they want.
 */
function onLaunch(launchRequest, session, callback) {
    console.log("onLaunch requestId=" + launchRequest.requestId + ", sessionId=" + session.sessionId);

    // Dispatch to your skill's launch.
    getWelcomeResponse(callback);
}

/**
 * Called when the user specifies an intent for this skill.
 */
function onIntent(intentRequest, session, callback) {
    console.log("onIntent requestId=" + intentRequest.requestId + ", sessionId=" + session.sessionId);

    var intent = intentRequest.intent,
        intentName = intentRequest.intent.name;

    // Dispatch to your skill's intent handlers
    if ("GetTemperature" === intentName) {
        getTemperature(intent, session, callback);
    } else if ("GetPulse" === intentName) {
        getPulse(intent, session, callback);
    } else if ("GetBoth" == intentName) {
        getBoth(intent, session, callback);
    } else if ("AMAZON.HelpIntent" === intentName) {
        getHelp(callback);
    } else if ("AMAZON.StopIntent" === intentName || "AMAZON.CancelIntent" === intentName) {
        handleSessionEndRequest(callback);
    } else {
        throw "Invalid intent";
    }
}

/**
 * Called when the user ends the session.
 * Is not called when the skill returns shouldEndSession=true.
 */
function onSessionEnded(sessionEndedRequest, session) {
    console.log("onSessionEnded requestId=" + sessionEndedRequest.requestId +
        ", sessionId=" + session.sessionId);
    // Add cleanup logic here
}

// --------------- Functions that control the skill's behavior -----------------------

function getWelcomeResponse(callback) {
    var sessionAttributes = {};
    var cardTitle = "Welcome";
    var speechOutput = "Welcome to Hospital Room 1, Where I communicate with some sensors in the hospital running from a raspberry pie," + 
    "Would you like to know the temperature or pulse rate?";
    var repromptText = "Would you like to know the temperature or pulse rate?";
    var shouldEndSession = false;

    callback(sessionAttributes, buildSpeechletResponse(cardTitle, speechOutput, repromptText, shouldEndSession));
}

function getHelp(callback) {
    var cardTitle = "Help";
    var speechOutput = "Welcome to Hospital Room 1, Where I communicate with some sensors in the hosptial running from a raspberry pie," + 
    "You can ask me what the temerature or humidity is, or ask about the weather for both.";
    var repromptText = "Would you like to know the temperature or pulse rate?";
    var shouldEndSession = false;

    callback(sessionAttributes, buildSpeechletResponse(cardTitle, speechOutput, repromptText, shouldEndSession));
}

function handleSessionEndRequest(callback) {
    var cardTitle = "Session Ended";
    var speechOutput = "Thank you for visiting Nick's House, Have a nice day!";
    var shouldEndSession = true;
    callback({}, buildSpeechletResponse(cardTitle, speechOutput, null, shouldEndSession));
}

function getTemperature(intent, session, callback) {
   var cardTitle = "Temperature";
   var repromptText = "";
   var sessionAttributes = {};
   var shouldEndSession = true;

   var temp = 0;

   iotData.getThingShadow(config.params, function(err, data) {
      if (err)  {
           console.log(err, err.stack); // an error occurred
      } else {
           //console.log(data.payload);           // successful response
           payload = JSON.parse(data.payload);
           temp = payload.state.desired.temperature;
      }

      speechOutput = "The temperature is " + temp + " degrees celcius";
      callback(sessionAttributes, buildSpeechletResponse(cardTitle, speechOutput, repromptText, shouldEndSession));
   });
}

function getPulse(intent, session, callback) {
   var cardTitle = "Temperature";
   var repromptText = "";
   var sessionAttributes = {};
   var shouldEndSession = true;

   var pulse = 0;

   iotData.getThingShadow(config.params, function(err, data) {
      if (err)  {
           console.log(err, err.stack); // an error occurred
      } else {
           //console.log(data.payload);           // successful response
           payload = JSON.parse(data.payload);
           pulse = payload.state.desired.pulse;
      }

      speechOutput = "The pulse is " + pulse + " beats.";
      callback(sessionAttributes, buildSpeechletResponse(cardTitle, speechOutput, repromptText, shouldEndSession));
   });
}

function getBoth(intent, session, callback) {
   var cardTitle = "Temperature";
   var repromptText = "";
   var sessionAttributes = {};
   var shouldEndSession = true;

   var temp = 0; 
   var pulse = 0;
   
   iotData.getThingShadow(config.params, function(err, data) {
      if (err)  {
           console.log(err, err.stack); // an error occurred
      } else {
           //console.log(data.payload);           // successful response
           payload = JSON.parse(data.payload);
           temp = payload.state.desired.temperature;
           pulse = payload.state.desired.pulse;
      }

      speechOutput = "The temperature is " + temp + " degrees celcius and the pulse is " + pulse + " beats";
      callback(sessionAttributes, buildSpeechletResponse(cardTitle, speechOutput, repromptText, shouldEndSession));
   });
}

// --------------- Helpers that build all of the responses -----------------------
function buildSpeechletResponse(title, output, repromptText, shouldEndSession) {
    return {
        outputSpeech: {
            type: "PlainText",
            text: output
        },
        card: {
            type: "Simple",
            title: title,
            content: output
        },
        reprompt: {
            outputSpeech: {
                type: "PlainText",
                text: repromptText
            }
        },
        shouldEndSession: shouldEndSession
    };
}

function buildResponse(sessionAttributes, speechletResponse) {
    return {
        version: "1.0",
        sessionAttributes: sessionAttributes,
        response: speechletResponse
    };
}
