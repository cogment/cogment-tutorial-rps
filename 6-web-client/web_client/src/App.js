// Copyright 2021 AI Redefined Inc. <dev+cogment@ai-r.com>
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import React, { useEffect, useState } from "react";
import { Box, Container } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { styled } from "@mui/system";
//Then some imports for icons and Material UI functionality we'll be using
import ComputerIcon from "@mui/icons-material/Computer";
import PersonIcon from "@mui/icons-material/Person";
//Second is our 'cogSettings'. This is a file that was generated when you ran
//`cogment generate --js_dir=./webclient`
//This file tells our web client relevant information about our trials, environments, and actor classes
import { cogSettings } from "./CogSettings";
import { Header } from "./components/Header";
//Finally here are two components which we will make later in the tutorial
import { Player } from "./components/Player";
//These are messages which were defined in data.proto, these imports will need to change whenever their corresponding messages in data.proto are changed, and cogment generate is run.
import { rps as PB } from "./data_pb";
//And here's the important part, we're importing the two things that will allow us to use cogment, first is the 'useActions' hook, this will give us the observations of our human agent, as well as allow us to make actions.
import { useActions } from "./hooks/useActions";

const CustomContainer = styled(Container)({
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
});

function getMoveText(move) {
  switch (move) {
    case 0:
      return "rock";
    case 1:
      return "paper";
    case 2:
      return "scissors";
    default:
      throw new Error("Not a rock, paper, or scissors");
  }
}

export const App = () => {
  //Bring in themes to use in Material UI
  const theme = useTheme();

  /*
      The most important part of our application.
  
      Here, we use the 'useActions' hook, this hook returns an array with 3 elements
  
      event: this contains all the information about any observation, reward, or message we've recieved this tick, we will use this to see what moves we and the computer played
  
      startTrial: this is a function which takes no arguments, and is a very simple way to start a new trial with our player actor
  
      sendAction: this is a funciton which takes an argument of type 'Action', this class can be imported from data_pb.js, but we'll see that later in this tutorial.
  
      This hook takes in 3 arguments, the first being
  
      cogSettings: this is what's imported from CogSettings.js, it provides all the relevant information about data.proto to this hook so that it can function
  
      actorName: the name of the human actor which this web client will be representing, this is defined in cogment.yaml

      actorClass: the class of the human actor which this web client will be representing, this is defined in cogment.yaml
    */
  const [event, startTrial, sendAction] = useActions(
    cogSettings,
    "player_1",
    "player"
  );

  //Function to construct the Action which the player will send when they click either rock, paper, or scissors
  const choose = (move) => {
    const action = new PB.PlayerAction({
      move
    });
    sendAction(action);
  };

  //This will start a trial as soon as we're connected to the orchestrator
  useEffect(() => {
    if (startTrial) startTrial();
  }, [startTrial]);

  //Get any observation from the current event, events have observations, messages, and rewards, and all three can be unpacked from the event object
  //We will also unpack a helpful variable called 'last', this will allow us to know when the trial has ended
  const { observation, last } = event;

  const [gameState, setGameState] = useState({
    gameStage: "start",
    roundIndex: 0,
    lastMoveComputer: 0,
    lastMoveHuman: 0,
  });
  const [firstObservation, setFirstObservation] = useState(true);

  useEffect(() => {
    //Parse game state out of the observation
    //Some events don't contain an observation, so we need to store the observation contents in a state
    if (!observation) return;

    //The first observation is not useful, as it just contains the default game state, before players have made moves
    if (firstObservation) {
      setFirstObservation(false);
      return;
    }

    //Get all relevant information from the observation
    const roundIndex = gameState.roundIndex + 1;
    const gameStage = "playing";
    const lastMoveComputer = observation.them.lastMove;
    const lastMoveHuman = observation.me.lastMove;
    const lastWonComputer = observation.them.wonLast;
    const lastWonHuman = observation.me.wonLast;

    setGameState({
      gameStage,
      roundIndex,
      lastMoveComputer,
      lastMoveHuman,
      lastWonComputer,
      lastWonHuman,
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [observation]);

  //If the the value of 'last' changes, see if it is true, and if so set the gameStage to 'end'
  useEffect(() => {
    if (!last) return;

    const newGameState = { ...gameState };
    newGameState.gameStage = "end";

    setGameState(newGameState);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [last]);

  //The layout of the page
  return (
    <Box>
      {/* <Typography>Game stage: {gameState.gameStage}</Typography>
            <Typography>Human's move: {gameState.gameStage !== "start" && getMoveText(gameState.lastMoveHuman)}</Typography>
            <Typography>Computer's move: {gameState.gameStage !== "start" && getMoveText(gameState.lastMoveComputer)}</Typography>
            <Typography>Did Human win last round? {observation && gameState.lastWonHuman ? "Yes" : "No"}</Typography>
            <Typography>Did Computer win last round? {observation && gameState.lastWonComputer ? "Yes" : "No"}</Typography>
            <Button onClick={() => choose(0)}>Rock</Button>
            <Button onClick={() => choose(1)}>Paper</Button>
            <Button onClick={() => choose(2)}>Scissors</Button> */}

      <Header gameState={gameState} />
      <CustomContainer>
        <Player
          color={theme.palette.primary.main}
          IconClass={PersonIcon}
          choose={choose}
          isHuman
        />

        <Player
          color={theme.palette.secondary.main}
          IconClass={ComputerIcon}
          selected={
            gameState.gameStage !== "start" &&
            getMoveText(gameState.lastMoveComputer)
          }
        />
      </CustomContainer>
    </Box>
  );
};
