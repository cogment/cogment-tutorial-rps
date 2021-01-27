import React, {useEffect} from 'react'

import ComputerIcon from "@material-ui/icons/Computer"
import PersonIcon from "@material-ui/icons/Person"
import { Container, makeStyles, useTheme } from '@material-ui/core';

import { useActions } from "../hooks/useActions";
import { Player } from './Player';
import cogSettings from '../cog_settings';
import { Header } from './Header';

const useStyles = makeStyles(theme => ({
    root: {
        backgroundColor: theme.palette.primary.light,
        width: "100vw",
        height: "100vh"
    },

    container: {
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
    },

    choiceButtonContainer: {
        display: "flex",
        justifyContent: "center"
    },

    choiceContainer: {
        margin: theme.spacing(1)
    },

    choiceImg: {
        paddingRight: "1vw",
        width: "12vw",
        height: "12vw"
    }
}));

function getMoveText(move){
    switch(move){
        case 0:
            return "rock"
        case 1:
            return "paper"
        case 2:
            return "scissors"
        default:
            throw new Error("Not a rock, paper, or scissors")
    }
}

export const RPS = () => {

    const classes = useStyles();
    const theme = useTheme();

    const [event, startTrial, sendAction] = useActions(cogSettings, "player_1", "player")

    useEffect(() => {
        console.log(startTrial);
        if(startTrial) startTrial();
    }, [startTrial])

    const { observation } = event;

    //Parse game state out of the observation
    let gameState;
    if(!observation || observation.roundIndex === 0) gameState = "start";
    if(observation && (observation.roundIndex !== 0)) gameState = "playing";
    if(observation && (observation.roundIndex === 0 && observation.gameIndex !== 0)) gameState = "end";

    //Get the button the AI has selected
    const AISelected = gameState !== "start" && getMoveText(observation.them.lastRoundMove)

    return (
        <>
            <Header observation={observation} gameState={gameState}/>
            <Container className={classes.container}>
                <Player score={observation ? observation.me.currentGameScore : 0} 
                        color={theme.palette.primary.main} 
                        IconClass={PersonIcon} 
                        onAction={sendAction} 
                        isHuman/>

                <Player score={observation ? observation.them.currentGameScore : 0} 
                        color={theme.palette.secondary.main} 
                        IconClass={ComputerIcon} 
                        selected={AISelected}/>
            </Container>
        </>
    )
}
