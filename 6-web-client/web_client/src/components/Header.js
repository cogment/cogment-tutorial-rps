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

import React from "react";

//Just some imports from Material UI for the styling, as well as some icons that we'll be using
import { SvgIcon, Typography } from "@mui/material";
import { styled } from "@mui/system";
import ComputerIcon from "@mui/icons-material/Computer";
import PersonIcon from "@mui/icons-material/Person";

const Banner = styled('div')(({ theme }) => ({
  backgroundColor: theme.palette.primary.main,
  padding: theme.spacing(4),
  marginBottom: theme.spacing(4),
  display: 'flex',
  flexDirection: 'row',
  justifyContent: 'center',
}));

const HeaderText = styled(Typography, {
  variant: 'h1',
  align:'center',
})({
  display: 'flex',
  alignItems: 'center',
});

const Spacer = styled('div')({
  display: 'flex',
  alignItems: 'center',
});

const InlineImg = styled('img')({
  width: '15vw',
  height: '15vw',
  margin: '0 0.25em',
});

const InlineIcon = styled(SvgIcon)({
  width: '15vw',
  height: '15vw',
  margin: '0 0.25em',
  fontSize: 'inherit',
});

export const Header = ({ gameState }) => {
  //Define icons we will be using, for simple access later in the component
  const rock = (
    <InlineImg
      alt="rock"
      src={"images/hand-rock.svg"}
    />
  );
  const paper = (
    <InlineImg
      alt="paper"
      src={"images/hand-paper.svg"}
    />
  );
  const scissors = (
    <InlineImg
      alt="scissors"
      src={"images/hand-scissors.svg"}
    />
  );
  const human = <InlineIcon><PersonIcon /></InlineIcon>;
  const computer = <InlineIcon><ComputerIcon /></InlineIcon>;

  //Simple function to go from enum to an image, this is the similar to the function in App.js that did something similar
  function getMoveImg(move) {
    switch (move) {
      case 0:
        return rock;
      case 1:
        return paper;
      case 2:
        return scissors;
      default:
        throw new Error("Not a rock, paper, or scissors");
    }
  }

  return (
    <Banner>
      {/*
          Show different information based on game state
          For the first option, if the game stage is just starting, tell the human to chose rock, paper, or scissors
        */}
      {gameState.gameStage === "start" && (
        <HeaderText>
          Pick{rock},{paper}, or{scissors}
        </HeaderText>
      )}

      {/*
          If the game stage is in the middle of playing, let the human know what the result of the last round was
        */}
      {gameState.gameStage === "playing" && (
        <HeaderText>
          {/*
              Show what each player chose as their action
            */}
            {human}
            {getMoveImg(gameState.lastMoveHuman)}
          <Spacer />
          {computer}
          {getMoveImg(gameState.lastMoveComputer)}
          <Spacer />
          {/*
              Show the result of each player choosing the aformentioned actions, either the human wins the round, computer wins the round, or it's a tie
            */}
          {gameState.lastWonHuman === gameState.lastWonComputer && "Tie!"}

          {gameState.lastWonHuman && !gameState.lastWonComputer && (
            <>{human}Won!</>
          )}

          {!gameState.lastWonHuman && gameState.lastWonComputer && (
            <>{computer}Won!</>
          )}
        </HeaderText>
      )}
      {/*
          If the game stage is end, tell the player
        */}
      {gameState.gameStage === "end" && (
        <HeaderText>
          Game Done!
        </HeaderText>
      )}
    </Banner>
  );
};
