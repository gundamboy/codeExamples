import React, { Component } from 'react';
import { connect } from 'react-redux';
import { Redirect } from 'react-router-dom';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import { handleAddQuestion } from '../actions/questions';

class NewQuestion extends Component {
    state = {
        optionOne: '', // keep track of OptionOne input
        optionTwo: '', // keep track of OptionTwo input
        toHome: false  // used to redirect user to home when question is added
    }

    handleChange = (option,e) => { // Update state on input fields value change
        const input = e.target.value;

        this.setState(() => ({ 
            [option]: input
        }))
    }

    handleSubmit = (e) => { // To handle form submit
        e.preventDefault();

        const { optionOne, optionTwo } = this.state;
        const { dispatch } = this.props;

        dispatch(handleAddQuestion(optionOne, optionTwo));

        this.setState(() => ({
            toHome: true // Trigger redirect user to homepage
        }))
        
    }

    render() {
        const { optionOne, optionTwo, toHome } = this.state;

        if(toHome) // Check if question is already added and redirect user to home
            return <Redirect to='/' />

        return (
            <div className="component-container">
                <Typography variant="title" gutterBottom>
                    Would you rather?
                </Typography>
                <form onSubmit={this.handleSubmit} className='form-container'>
                    <TextField
                        type="text"
                        label="Option One"
                        defaultValue={optionOne}
                        onChange={(e) => this.handleChange('optionOne',e)}
                        margin="normal"
                        fullWidth
                        autoFocus
                    />
                    <TextField
                        type="text"
                        label="Option Two"
                        defaultValue={optionTwo}
                        onChange={(e) => this.handleChange('optionTwo',e)}
                        margin="normal"
                        fullWidth
                    />
                    <Button variant="contained" color="primary" 
                        type="submit"
                        disabled={!optionOne || !optionTwo}
                    >
                        Add Question
                    </Button>
                </form>
            </div>
        )
    }
}

export default connect()(NewQuestion);