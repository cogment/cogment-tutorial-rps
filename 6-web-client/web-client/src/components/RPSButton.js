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

import React from 'react'

import { IconButton, makeStyles, useTheme } from '@material-ui/core'

const useStyles = makeStyles({
    choiceButton: {
        width: "15vw",
        height: "15vw",
        backgroundColor: props => props.color,
        pointerEvents: props => (props.isHuman ? "all" : "none"),

        "&:hover": {
            backgroundColor: props => props.color,
            border: "2px solid black"
        }
    },

    choiceButtonGray: {
        width: "15vw",
        height: "15vw",
        backgroundColor: "#888888",
        pointerEvents: props => (props.isHuman ? "all" : "none")
    },

    choiceImg: {
        width: "12vw",
        height: "12vw",
        paddingRight: "1vw",
    }
})

export const RPSButton = ({ selected, isHuman, move, onClick}) => {
    const theme = useTheme();

    const color = isHuman ? theme.palette.primary.main : theme.palette.secondary.main
    const classes = useStyles({color, isHuman})
    
    const className = isHuman || selected ? classes.choiceButton : classes.choiceButtonGray

    return (
        <IconButton className={className} 
                    onClick={onClick}>
            <img alt={(isHuman ? "Human " : "Computer ") + move} className={classes.choiceImg} src={"images/hand-" + move + ".svg"} />
        </IconButton>
    )
}
