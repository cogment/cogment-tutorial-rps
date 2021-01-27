import { makeStyles, Typography } from '@material-ui/core';
import React from 'react'

import ComputerIcon from "@material-ui/icons/Computer"
import PersonIcon from "@material-ui/icons/Person"

const useStyles = makeStyles(theme => ({
    banner: {
        backgroundColor: theme.palette.primary.main,
        padding: theme.spacing(4),
        marginBottom: theme.spacing(4),
        display: "flex",
        flexDirection: "row",
        justifyContent: "center"
    },

    inlineImg:{
        height: "1em",
        width: "1em",
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

export const Header = ({observation, gameState}) => {
    
    const classes = useStyles();

    const rock = <img alt="rock" className={classes.inlineImg} src={"images/hand-rock.svg"} />
    const paper = <img alt="paper" className={classes.inlineImg} src={"images/hand-paper.svg"} />
    const scissors = <img alt="scissors" className={classes.inlineImg} src={"images/hand-scissors.svg"} />
    const human = <PersonIcon className={classes.inlineImg}/>
    const computer = <ComputerIcon className={classes.inlineImg}/>

    //Go from enum, to coresponding move image
    function getMoveImg(move){
        switch(move){
            case 0:
                return rock;
            case 1:
                return paper;
            case 2:
                return scissors;
            default:
                throw new Error("Not a rock, paper, or scissors")
        }
    }

    //Get the text for who won the round
    let winText

    if(gameState === "playing"){
        const tie = observation.me.lastRoundWin === observation.them.lastRoundWin

        //There's &nbsp; everywhere because of how jsx treats whitespace. The alternative looks even worse
        winText = tie ? "Tie!" : <>
            {observation.me.lastRoundWin && <>{human}&nbsp;Won!</>}
            {observation.them.lastRoundWin && <>{computer}&nbsp;Won!</>}
        </>
    }

    return (
        <div className={classes.banner}>
            {gameState === "start" && <Typography variant="h1" align="center" className={classes.headerText}>Pick&nbsp;{rock},&nbsp;{paper},&nbsp;or&nbsp;{scissors}</Typography>}
            {gameState === "playing" && 
                <Typography variant="h1" align="center" className={classes.headerText}>
                    {human}&nbsp;{getMoveImg(observation.me.lastRoundMove)}
                    <div className={classes.spacer}/>
                    {computer}&nbsp;{getMoveImg(observation.them.lastRoundMove)}
                    <div className={classes.spacer}/>
                    {winText}
                </Typography>
            }
            {gameState === "end" && 
                <Typography variant="h1" align="center" className={classes.headerText}>
                    {observation.me.currentGameScore > observation.them.currentGameScore && human}
                    {observation.me.currentGameScore < observation.them.currentGameScore && computer}
                    &nbsp;WINS!
                    <div className={classes.spacer}/>
                    Choose to play again
                </Typography>
            }
        </div>
    )
}
