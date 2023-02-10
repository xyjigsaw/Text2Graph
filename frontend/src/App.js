import './App.css';
import Graph from "react-graph-vis";
import React, { useState } from "react";
const options = {
  layout: {
    hierarchical: false
  },
  edges: {
    color: "#34495e"
  }
};

function App() {
  const [state, setState] = useState(
    {
      counter: 0,
      graph: {
        nodes: [],
        edges: []
      }
    })
  const { graph } = state;

  const clearState = () => {
    setState({
      counter: 0,
      graph: {
        nodes: [],
        edges: []
      }
    })
  }

  const queryPrompt = (prompt) => {
    console.log(prompt)

    fetch('http://127.0.0.1:8000/get_graph?text=' + prompt)
        .then(response => {
          if (!response.ok) {
            throw new Error('Something went wrong with the request, please check the Network log');
          }
          return response.json();
        })
        .then((response) => {
          const text = response.data;
          console.log(text);
          const new_graph = text;
          console.log(new_graph);
          setState(new_graph, () => {
            console.log(state);
          });
          document.body.style.cursor = 'default';
          document.getElementsByClassName("generateButton")[0].disabled = false;
          document.getElementsByClassName("searchBar")[0].value = "";
        }).catch((error) => {
      console.log(error);
      alert(error);
      document.body.style.cursor = 'default';
      document.getElementsByClassName("generateButton")[0].disabled = false;
    });
  }


  const createGraph = () => {
    document.body.style.cursor = 'wait';

    document.getElementsByClassName("generateButton")[0].disabled = true;
    const prompt = document.getElementsByClassName("searchBar")[0].value;

    queryPrompt(prompt);
  }

  return (
    <div className='container'>
      <h1 className="headerText">Text2Graph-T5 🔎</h1>
      <p className='subheaderText'>Build complex, directed graphs to add structure to your ideas using natural language. Understand the relationships between people, systems, and maybe solve a mystery.</p>
      <center>
        <div className='inputContainer'>
          <input className="searchBar" placeholder="Describe your graph..."></input>
          <button className="generateButton" onClick={createGraph}>Generate</button>
          <button className="clearButton" onClick={clearState}>Clear</button>
        </div>
      </center>
      <div className='graphContainer'>
        <Graph graph={graph} options={options} style={{ height: "640px" }} />
      </div>
      <p className='footer'>Pro tip: don't take a screenshot! You can right-click and save the graph as a .png  📸</p>
    </div>
  );
}

export default App;
