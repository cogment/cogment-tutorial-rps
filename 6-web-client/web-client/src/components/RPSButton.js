import { IconButton, makeStyles } from '@material-ui/core'
import React from 'react'

import { Move } from '../data_pb';

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
        paddingRight: "1vw",
        width: "12vw",
        height: "12vw"
    }
})

export const RPSButton = ({ hovered, isHuman, color, move, onHovered, onChoose}) => {
    const classes = useStyles({color, isHuman})

    return (
        <IconButton className={hovered === move || hovered === null ? classes.choiceButton : classes.choiceButtonGray} 
                    //Move[move.toUpperCase()] selects the proper enum from data_pb
                    onClick={() => onChoose(Move[move.toUpperCase()])}
                    onMouseEnter={() => onHovered(move)}
                    onMouseLeave={() => onHovered(null)}>
            <img alt={(isHuman ? "Human " : "Computer ") + move} className={classes.choiceImg} src={"images/hand-" + move + ".svg"} />
        </IconButton>
    )
}
