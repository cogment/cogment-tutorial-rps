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
import { makeStyles, Typography } from "@material-ui/core";
import ComputerIcon from "@material-ui/icons/Computer";
import PersonIcon from "@material-ui/icons/Person";

const useStyles = makeStyles(theme => ({
    banner: {
        backgroundColor: theme.palette.primary.main,
        padding: theme.spacing(4),
        marginBottom: theme.spacing(4),
        display: "flex",
        flexDirection: "row",
        justifyContent: "center"
    },

    inlineImg: {
        height: "1em",
        width: "1em",
        margin: "0 0.25em",
        fontSize: "inherit"
    },

    headerText: {
        display: "flex",
        alignItems: "center"
    },

    spacer: {
        width: "1em"
    }
}));

export const Header = ({ gameState }) => {
    //Get styles
    const classes = useStyles();

    //Define icons we will be using, for simple access later in the component
    const rock = (
        <img
            alt="rock"
            className={classes.inlineImg}
            src={"images/hand-rock.svg"}
        />
    );
    const paper = (
        <img
            alt="paper"
            className={classes.inlineImg}
            src={"images/hand-paper.svg"}
        />
    );
    const scissors = (
        <img
            alt="scissors"
            className={classes.inlineImg}
            src={"images/hand-scissors.svg"}
        />
    );
    const human = <PersonIcon className={classes.inlineImg} />;
    const computer = <ComputerIcon className={classes.inlineImg} />;

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
        <div className={classes.banner}>
            {/*
          Show different information based on game state
          For the first option, if the game stage is just starting, tell the human to chose rock, paper, or scissors
        */}
            {gameState.gameStage === "start" && (
                <Typography variant="h1" align="center" className={classes.headerText}>
                    Pick{rock},{paper}, or{scissors}
                </Typography>
            )}

            {/*
          If the game stage is in the middle of playing, let the human know what the result of the last round was
        */}
            {gameState.gameStage === "playing" && (
                <Typography variant="h1" align="center" className={classes.headerText}>
                    {/*
              Show what each player chose as their action
            */}
                    {human}
                    {getMoveImg(gameState.lastMoveHuman)}
                    <div className={classes.spacer} />
                    {computer}
                    {getMoveImg(gameState.lastMoveComputer)}
                    <div className={classes.spacer} />

                    {/*
              Show the result of each player choosing the aformentioned actions, either the human wins the round, computer wins the round, or it's a tie
            */}
                    {gameState.lastWonHuman === gameState.lastWonComputer &&
                        "Tie!"}

                    {gameState.lastWonHuman && !gameState.lastWonComputer && (
                        <>{human}Won!</>
                    )}

                    {!gameState.lastWonHuman && gameState.lastWonComputer && (
                        <>{computer}Won!</>
                    )}
                </Typography>
            )}
            {/*
          If the game stage is end, tell the player
        */}
            {gameState.gameStage === "end" && (
                <Typography variant="h1" align="center" className={classes.headerText}>
                    Games Done!
                </Typography>
            )}
        </div>
    );
};