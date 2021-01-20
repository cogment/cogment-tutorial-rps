import React, { useState } from 'react'
import Grid from "@material-ui/core/Grid";
import { makeStyles, Typography } from '@material-ui/core';
import { Action } from '../data_pb';
import { RPSButton } from './RPSButton';

const useStyles = makeStyles(theme => ({

    icon: {
        width: "8vw",
        height: "8vw",
        paddingRight: "1vw",
        pointerEvents: "none"
    },

    choiceButtonContainer: {
        display: "flex",
        justifyContent: "center",
        alignItems: "center "
    },

    choiceContainer: {
        margin: theme.spacing(1)
    }
}));

export const Player = ({ color, IconClass, score=0, isHuman, onAction, selected }) => {
    const classes = useStyles({color, isHuman});

    function choose (move){
        const action = new Action();
        action.setMove(move);
        onAction(action);
    }
    
    let [hovered, setHovered] = useState(null);
    
    //If this is a non-human agent, the hovered button is set by the props
    if(!isHuman){
        hovered = selected;
    }

    return (
        <Grid className={classes.choiceContainer} container>
            <Grid className={classes.choiceButtonContainer} item xs={3}>
                <IconClass className={classes.icon} />
                <Typography variant="h1">{score}</Typography>
            </Grid>
            

            <Grid className={classes.choiceButtonContainer} item xs={3}>
                <RPSButton hovered={hovered} color={color} move="rock" isHuman={isHuman} onChoose={choose} onHovered={setHovered}/>
            </Grid>

            <Grid className={classes.choiceButtonContainer} item xs={3}>
                <RPSButton hovered={hovered} color={color} move="paper" isHuman={isHuman} onChoose={choose} onHovered={setHovered}/>
            </Grid>

            <Grid className={classes.choiceButtonContainer} item xs={3}>
                <RPSButton hovered={hovered} color={color} move="scissors" isHuman={isHuman} onChoose={choose} onHovered={setHovered}/>
            </Grid>
        </Grid>
    )
}
