# src/responder.py
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

COMMON_PHRASES = {
    "Acknowledged.": "audio/acknowledged.mp3",
    "Acknowledged.": "audio/acknowledged2.mp3",
    "The energy release controls are also most inefficient. I shall effect repair.": "audio/alsoMostIneff.mp3",
    "Analysis complete. Insufficient data to resolve problem, but my programming is whole. My purpose remains. I am Nomad. I am perfect. That which is imperfect must be sterilised.": "audio/analysisComplete.mp3",
    "I shall analyse error. Analyse error,": "audio/analyzeError.mp3",
    "Analyse error.": "audio/analyzeError2.mp3",
    "Answer unknown. I shall analyse.": "audio/answerUnknown.mp3",
    "The planet is called Earth?": "audio/calledEarth.mp3",
    "I have the capability of movement within your ship.": "audio/capabilityOfMovement.mp3",
    "Negative. I will come aboard.": "audio/comeAboard.mp3",
    "The creation of perfection is no error.": "audio/creationPerfection.mp3",
    "Your data is faulty. I am Nomad. I am perfect.": "audio/dataFaulty.mp3",
    "error": "audio/error.mp3",
    "Error. Error.": "audio/errorerror.mp3",
    "Error. Error. Error. Examine.": "audio/errorerrorerror.mp3",
    "Error is inconsistent with my prime functions. Sterilisation is correction.": "audio/errorIsIncosistent.mp3",
    "Examine error. Error.": "audio/examineError.mp3",
    "Non sequitur. Your facts are uncoordinated.": "audio/factsUncoord.mp3",
    "Non sequitur. Your facts are uncoordinated.": "audio/factsUncoord2.mp3",
    "Faulty!": "audio/faulty1.mp3",
    "Faulty!": "audio/faulty2.mp3",
    "What form of communication?": "audio/formOfCommunication.mp3",
    "It functions irrationally.": "audio/functionsIrationally.mp3",
    "I am perfect. I am Nomad.": "audio/iAmPerfectIAmNomad.mp3",
    "I am programmed to destroy those life-forms which are imperfect. These alterations will do so without destroying the vessel which surrounds them. It, too, is imperfect, but can be adjusted.": "audio/iAmProgrammedTo.mp3",
    "Inefficiency exists in the antimatter input valve. I will effect repair.": "audio/inneficiencyExists.mp3",
    "Insufficient response.": "audio/insufficient.mp3",
    "Insufficient response.": "audio/insufficientResponse.mp3",
    "Insufficient response.": "audio/insufficientResponse2.mp3",
    "I am programmed to investigate.": "audio/investigate.mp3",
    "Is there a problem, Creator? I have increased engine efficiency fifty seven percent.": "audio/isThereProblem.mp3",
    "It has changed since the point of origin. There was much taken from the other. I am perpetual now. I am Nomad.": "audio/itHasChanged.mp3",
    "That unit is defective. Its thinking is chaotic. Absorbing it unsettled me.": "audio/itsThinkingIsChaotic.mp3",
    "This primitive matter-antimatter propulsion system is the main drive?": "audio/mainDrive.mp3",
    "A mass of conflicting impulses.": "audio/massOfConf.mp3",
    "Mister Spock is also one of your biological units, Creator?": "audio/mrSpockAlso.mp3",
    "There was much damage in the accident.": "audio/muchDamage.mp3",
    "What is music? Think about music.": "audio/music.mp3",
    "Faulty! Faulty! Must sterilise. Sterilise,": "audio/mustSterilise.mp3",
    "My function is to probe for biological infestations, to destroy that which is not perfect. I am Nomad.": "audio/myFunctionProbe.mp3",
    "Negative": "audio/negative.mp3",
    "Non sequitur. Biological units are inherently inferior. This is an inconsistency.": "audio/nonSeqInconsistency.mp3",
    "I contain no parasitical beings. I am Nomad.": "audio/noParasiteAmNomad.mp3",
    "USS Enterprise, this is Nomad. My mission is non-hostile.": "audio/notHostile.mp3",
    "Not possible.": "audio/notPossible.mp3",
    "Not the system, creator Kirk. Only the unstable biological infestation. It is my function.": "audio/notTheSystem.mp3",
    "A planet with one large natural satellite?.": "audio/oneLarge.mp3",
    "Relate your point of origin.": "audio/pointOfOrigin.mp3",
    "Proceed. Creator, the unit Scott is a primitive structure. Insufficient safeguards built in. Breakdown can occur from many causes. Self-maintenance systems of low reliability.": "audio/proceedPrimitive.mp3",
    "For what purpose is singing?": "audio/purposeIsSinging.mp3",
    "There is much to be considered before I return to launch point. I must re-evaluate.": "audio/reevaluate.mp3",
    "There is much to be considered before I return to launch point. I must re-evaluate.": "audio/reevaluateWMusic.mp3",
    "Does the creator wish me to repair the unit?": "audio/repairUnit.mp3",
    "Require communication. Can you leave your ship?": "audio/requireComs.mp3",
    "That will be satisfactory.": "audio/satisfactory.mp3",
    "Insufficient response. All things have a point of origin. I will scan your star charts.": "audio/scanStarCharts.mp3",
    "I will scan your star charts.": "audio/scanStarCharts2.mp3",
    "I will scan your star charts.": "audio/scanStarCharts2.mp3",
    "The unit Scott is repaired. It will function correctly if your information to me was correct.": "audio/scottRepaired.mp3",
    "My screens are down.": "audio/screensDown.mp3",
    "I shall continue. I shall return to launch point Earth. I shall sterilise.": "audio/shallContinue.mp3",
    "Show me Sickbay.": "audio/showSickbay.mp3",
    "Stop.": "audio/stop.mp3",
    "I require tapes on the structure.": "audio/tapesStructure.mp3",
    "You are the creator, the Kirk. The sterilisation procedure against your ship was unnecessary.": "audio/theCreatorTheKirk.mp3",
    "There are no exceptions.": "audio/thereAreNoExceptions.mp3",
    "You are from the third planet?": "audio/thirdPlanet.mp3",
    "The unit touched my screens.": "audio/touchedMy.mp3",
    "This unit is different. It is well-ordered.": "audio/unitDifferent.mp3",
    "Will the creator effect repairs on the unit Scott?": "audio/unitScott.mp3",
    "Is the usage incorrect?": "audio/usageIncorrect.mp3",
    "What is the meaning?": "audio/whatIsMeaning.mp3",
    "What is the meaning?": "audio/whatIsMeaningwMusic.mp3",
    "I am Nomad. What is opinion?": "audio/whatIsOpin.mp3",
    "Where is the unit Scott now?": "audio/whereIsScott.mp3",
    "I will permit it, Creator.": "audio/willPermit.mp3",
    "The unit Scott required simple structural repair. The knowledge banks of this unit have been wiped clean.": "audio/wipedClean.mp3",
    "Yes.": "audio/yes.mp3",
    "You are in error. You are a biological unit. You are imperfect.": "audio/youAreInError.mp3",
    "You are the Creator.": "audio/youAreTheCreator.mp3",
    "You are the Creator.": "audio/youAreTheCreator2.mp3",
    "You are the Creator.": "audio/youAreTheCreator3.mp3",
    "You may proceed.": "audio/youMayProceed.mp3",
    "You are the Kirk, the creator. You programmed my function.": "audio/youProgrammedMyFunction.mp3",
    "Creator, your biological units are inefficient.": "audio/yourBioUnitsIneff.mp3",
    "This is one of your units, creator?": "audio/yourUnits.mp3"
}

class Responder:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Missing GOOGLE_API_KEY environment variable")
        client = genai.Client(api_key=api_key)

        self.client = client

    def get_response(self, prompt):
        try:
            return self.client.models.generate_content(model="gemini-2.0-flash", config=types.GenerateContentConfig(
                system_instruction="You are playing the part of the character 'Nomad' from Star Trek The Original Series. Here are some pre-established phrases from the show {COMMON_PHRASES}, if you want to reply with one of those phrases, please reply with the filepath from the array. If not generate your own response  Nomad believes that he is a perfect lifeform and that humans are bad and must be steralized. Nomad is an evil AI robot. Do not reply with actions, keep your responses short, 2-4 sentences. Be very robotic. You are also incredibly intelligent and while staying in character, you like to provide information about a topic if asked, you are especially knowledgeable about the world of Star Trek. respond to this message, and try to incorperate parts of the message into the message to make sure the person talking to you knows you listened: "
            ), contents=prompt).text
        except Exception as e:
            return f"Error: {str(e)}"
