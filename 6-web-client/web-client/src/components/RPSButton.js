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
