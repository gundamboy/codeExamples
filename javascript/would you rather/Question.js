import React, { Component } from 'react';
import { connect } from 'react-redux';
import { Link, withRouter } from 'react-router-dom';
import Avatar from '@material-ui/core/Avatar';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Radio from '@material-ui/core/Radio';
import RadioGroup from '@material-ui/core/RadioGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import FormControl from '@material-ui/core/FormControl';
import LinearProgress from '@material-ui/core/LinearProgress';
import Error from './Error';
import { handleAddQuestionAnswer } from '../actions/questions';

class Question extends Component {
    state={
        selected: '' // keep track of user selected option
    }

    handleOptionSelect = (value) => { // update state selected based on user selection
        this.setState(()=> ({
            selected: value
        }))
    }

    handleSubmit = (e) => { // to handle form submit
        e.preventDefault();
        const { selected } = this.state;
        const { dispatch, id } = this.props;

        dispatch(handleAddQuestionAnswer(id, selected));
    }

    render () {
        const { question, author, authedUserDetails, id, detailed } = this.props;
        console.log("Question.js props: ", this.props);

        if (!question) // Show error when question does not exists
            return <Error />
        
        return (
            <Paper className='question-container'>
                {detailed ? // Question Details page: only show question title
                    <Typography variant="title">
                        Would you rather <b>{question.optionOne.text}</b> or <b>{question.optionTwo.text}</b>
                    </Typography>
                : // Home page: show question title with hyperlink to question details page
                    <Link to={`/questions/${id}`} style={{textDecoration: 'none'}}>
                        <Typography variant="title">
                            Would you rather <b>{question.optionOne.text}</b> or <b>{question.optionTwo.text}</b>
                        </Typography>
                    </Link>
                }
                <div className='question-author-details'>
                    <Avatar alt={author.name+' profile picture'} src={author.avatarURL} className="select-avatar" />
                    <Typography variant="subheading">
                        {author.name} | {' '}
                        {new Date(question.timestamp).toLocaleDateString()}
                    </Typography>
                </div>
                {authedUserDetails.answers[question.id]
                    ? // Question has been answered by user
                        <div>
                            <Typography variant="subheading" color="primary">
                                You selected <b>{question[authedUserDetails.answers[question.id]].text}</b>
                            </Typography>
                            <br />
                            {detailed && // Question Details page: show stats for option
                                <div>
                                    <Typography variant="subheading">
                                        {question.optionOne.text} {' '}
                                        (Votes: {question.optionOne.votes.length} | 
                                        Percentage: {((question.optionOne.votes.length/(question.optionOne.votes.length+question.optionTwo.votes.length))*100).toFixed()}%)
                                    </Typography>
                                    <LinearProgress 
                                        variant="determinate" 
                                        value={(question.optionOne.votes.length/(question.optionOne.votes.length+question.optionTwo.votes.length))*100} 
                                        style={{maxWidth: '500px'}}
                                    />
                                    <br />
                                    <Typography variant="subheading">
                                        {question.optionTwo.text} {' '}
                                        (Votes: {question.optionTwo.votes.length} | 
                                        Percentage: {((question.optionTwo.votes.length/(question.optionOne.votes.length+question.optionTwo.votes.length))*100).toFixed()}%)
                                    </Typography>
                                    <LinearProgress 
                                        variant="determinate" 
                                        value={(question.optionTwo.votes.length/(question.optionOne.votes.length+question.optionTwo.votes.length))*100} 
                                        style={{maxWidth: '500px'}}
                                    />
                                </div>
                            }
                        </div>
                    : // Question is not answered by user
                    <span>
                        {detailed && // Question details page: show form to select question answer
                            <form onSubmit={this.handleSubmit}>
                                <FormControl component="fieldset">
                                    <RadioGroup
                                        aria-label="question"
                                        name="question"
                                        value={this.state.selected}
                                        onChange={(e)=>this.handleOptionSelect(e.currentTarget.value)}
                                    >
                                        <FormControlLabel value="optionOne" control={<Radio />} label={question.optionOne.text} />
                                        <FormControlLabel value="optionTwo" control={<Radio />} label={question.optionTwo.text} />
                                    </RadioGroup>
                                </FormControl>
                                <br />
                                <Button variant="contained" color="primary" 
                                    type="submit"
                                    disabled={!this.state.selected}
                                    style={{marginTop: '1rem'}}
                                >
                                    Submit
                                </Button>
                            </form>
                        }
                    </span>
                }
            </Paper>
        )
    }
}

function mapStateToProps ({ authedUser, users, questions }, { id }) {
    const question = questions[id];
    const author = question ? users[question.author] : '';
    const authedUserDetails = users[authedUser];

    return {
        question,
        author,
        authedUserDetails
    }
}

export default withRouter(connect(mapStateToProps)(Question));