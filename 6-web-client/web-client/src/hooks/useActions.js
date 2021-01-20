import { useEffect, useState } from "react"
import {cogment}from "@ai-r/cogment-js-sdk"

export const useActions = (cogSettings, actorName, actorClass, userId) => {
    const [event, setEvent] = useState({observation: null, 
                                        message: null, 
                                        reward: null});

    const [startTrial, setStartTrial] = useState(null);                            
    const [sendAction, setSendAction] = useState(null);

    console.log(cogment);
    
    //Set up the connection and register the actor only once, regardless of re-rendering
    useEffect(() => {
        const service = cogment.createService(
            {cogSettings}
        )

        const actor = { name: actorName, class: actorClass };

        service.registerActor(
            actor,
            async (actorSession) => {
                actorSession.start();

                //Double arrow function here beause react will turn a single one into a lazy loaded function
                setSendAction(() => (action) => {
                    actorSession.sendAction(action);
                })

                for await (const {
                    observation,
                    message,
                    reward,
                } of actorSession.eventLoop()) {
                    //Parse the observation into a regular JS object
                    //TODO: this will eventually be part of the API
                    let observationOBJ = observation && observation.toObject();

                    setEvent({observation: observationOBJ, message, reward })
                }
            },
        );

        //Creating the trial controller must happen after actors are registered
        const trialController = service.createTrialController();
        
        //Need to output a function so that the user can start the trial when all actors are connected
        //Again, double arrow function cause react will turn a single one into a lazy loaded function
        setStartTrial(() => async () => {
            const { trialId } = await trialController.startTrial(actor.name)
            trialController.joinTrial(trialId, actor)
        })
    }, [cogSettings, actorName, actorClass])


    return [event, startTrial, sendAction];
}