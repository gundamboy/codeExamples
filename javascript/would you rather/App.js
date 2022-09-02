import React, { Component } from 'react';
import { BrowserRouter as Router, Route} from 'react-router-dom';
import { connect } from 'react-redux';
import LoadingBar from 'react-redux-loading';
import Typography from '@material-ui/core/Typography';
import { handleInitialData } from '../actions/shared';
import Dashboard from './Dashboard';
import Signin from './Signin';
import NewQuestion from './NewQuestion';
import QuestionDetails from './QuestionDetails';
import Leaderboard from './Leaderboard';
import Navbar from './Navbar';

class App extends Component {
  componentDidMount () {
    this.props.dispatch(handleInitialData());
  }
  render() {
    return (
      <Router>
        <div>
          <LoadingBar />
          <div className="header">
            <Typography variant="headline">
              Would You Rather
            </Typography>
            {this.props.signedIn && 
              <Navbar authedUser={this.props.authedUserName} authedUserAvatar={this.props.authedUserAvatar} />
            }
          </div>
          {
            !this.props.signedIn // Check whether user is signed in or not
            ? <Signin /> 
            : <div>
                <Route path='/' exact component={Dashboard} />
                <Route path='/questions/:id' component={QuestionDetails} />
                <Route path='/add' component={NewQuestion} />
                <Route path='/leaderboard' component={Leaderboard} />
              </div>
          }
        </div>
      </Router>
    );
  }
}

function mapStateToProps ({ authedUser, users }) {
  return {
    signedIn: authedUser !== null,
    authedUserName: authedUser ? users[authedUser].name : '',
    authedUserAvatar: authedUser ? users[authedUser].avatarURL : '',
  }
}

export default connect(mapStateToProps)(App);
