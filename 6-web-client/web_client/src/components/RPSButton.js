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

import { IconButton } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { styled } from "@mui/system";

const ChoiceButton = styled(IconButton)(
  props => ({
    width: '15vw',
    height: '15vw',
    backgroundColor: props.bgColor,
    pointerEvents: props.isHuman ? 'all' : 'none',
    '&:hover': {
      backgroundColor: props.bgColor,
      border: '2px solid black',
    },
  })
);

const ChoiceImg = styled('img')({
  width: '12vw',
  height: '12vw',
  paddingRight: '1vw',
});

export const RPSButton = ({ selected, isHuman, move, onClick }) => {
  const theme = useTheme();

  const playerColor = isHuman
    ? theme.palette.primary.main
    : theme.palette.secondary.main;
  
  const buttonBg = isHuman || selected ? playerColor : '#888888';

  return (
    <ChoiceButton onClick={onClick} bgColor={buttonBg} isHuman={isHuman}>
      <ChoiceImg
        alt={(isHuman ? "Human " : "Computer ") + move}
        src={"images/hand-" + move + ".svg"}
      />
    </ChoiceButton>
  );
};
