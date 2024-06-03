import React, {useEffect, useState} from 'react'
import './App.css'

const App = () => {
  const [users, setUsers] = useState([])
  useEffect (() =>{
    fetchData();
  },[])
  
  const fetchData = async () => {
    await fetch('https://jsonplaceholder.typeicode.com/users')
    .then((res) => res.json)
    .then((data) => setUsers(data))
    .catch((err) => {
        console.log(err);
    })
  }

  console.log(users)
  return (
    <div className='App'>
        <h3> React Crud Using Jsonplaceholder</h3>
    </div>
  )
}

export default App