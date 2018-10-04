import React, { Component } from "react";

import {
  NavLink,
  Switch
  } from "react-router-dom";
import 'react-table/react-table.css'
import './App.css';

class Home extends Component {

  constructor(props) {
    super(props);
    this.state = {
      error: null,
      isLoaded: false,
      result: []
    };
  }

  componentDidMount() {
    fetch("http://localhost:37722/api/v1/projects")
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            isLoaded: true,
            result: result,
          });
        },
        (error) => {
          this.setState({
            isLoaded: true,
            error
          });
        }
      )
  }

  render() {
    const { error, isLoaded, result } = this.state;
    var projects;
    projects = result;

    const List = props => <ul className="project-list">{props.children}</ul>;
    const ListItem = function(props) {
      return <li key={props.text} className="project-items">
        <h3>{props.text}</h3>
        <button><NavLink to={urlCreator(props.text, 'completed')}>Completed</NavLink></button>
        <button><NavLink to={urlCreator(props.text, 'queued')}>Queued</NavLink></button>
      </li>;

    }
    function urlCreator(name, status){
      const completedURL = `/projects/${name}/jobs/${status}`;
      return completedURL;
    }

    if (error && result[0]) {
      return <div>Error: {error.message}</div>;
    } else if (!isLoaded) { 
      return <div>Loading...</div>;
    } else if (result && result[0]) {
      return (
        <div className="home">
          <h3 className="project-source">Projects</h3>
            <List>
              {result.map(i => <Switch key={i.name}><ListItem text={i.name}/></Switch>)}
            </List>
        </div>
      );
    } else {
      return (
        <div>
          <h2>Project Listing</h2>
          <p>No project have been created––you should create one!</p>
          <p>Looking for docs, checking out the <a href="https://github.com/DeepLearnI/foundations/tree/master/examples">/examples directory</a></p>
        </div>
      );
    }
  }
}

export default Home;