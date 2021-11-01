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

//Material UI imports, for style
import Grid from "@material-ui/core/Grid";
import { makeStyles } from "@material-ui/core";

//One last component which we haven't defined yet, don't worry, it's not too big
import { RPSButton } from "./RPSButton";

const useStyles = makeStyles((theme) => ({
  icon: {
    width: "8vw",
    height: "8vw",
    paddingRight: "1vw",
    pointerEvents: "none",
  },

  choiceButtonContainer: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center ",
  },

  choiceContainer: {
    margin: theme.spacing(1),
  },
}));

//This component will recieve some props, which will tell it about the trial state, and whether it's the human, or computer player
export const Player = ({
  IconClass /*Either a human, or computer icon*/,
  isHuman /*Is the component a human?*/,
  choose,
  selected /*Which option is selected (Only relevant if this is representing the computer)*/,
}) => {
  const classes = useStyles({ isHuman });

  return (
    <Grid className={classes.choiceContainer} container>
      {/*
          Show for this player, whether they are the human, or the computer
        */}
      <Grid className={classes.choiceButtonContainer} item xs={3}>
        <IconClass className={classes.icon} />
      </Grid>

      {/*
          The Rock, Paper, and Scissors buttons
        */}
      <Grid className={classes.choiceButtonContainer} item xs={3}>
        <RPSButton
          selected={selected === "rock"}
          move="rock"
          onClick={() => choose(0)}
          isHuman={isHuman}
        />
      </Grid>

      <Grid className={classes.choiceButtonContainer} item xs={3}>
        <RPSButton
          selected={selected === "paper"}
          move="paper"
          onClick={() => choose(1)}
          isHuman={isHuman}
        />
      </Grid>

      <Grid className={classes.choiceButtonContainer} item xs={3}>
        <RPSButton
          selected={selected === "scissors"}
          move="scissors"
          onClick={() => choose(2)}
          isHuman={isHuman}
        />
      </Grid>
    </Grid>
  );
};
