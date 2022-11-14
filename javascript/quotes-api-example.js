import * as React from 'react';
import { useState, useEffect } from 'react';
import './style.css';

export default function App() {
    const [quotes, setQuotes] = useState([]);

    useEffect(() => {
        const getQuotes = async () => {
            const response = await fetch('https://dummyjson.com/quotes');
            const fetchedQuotes = await response.json();
            setQuotes(fetchedQuotes.quotes);
        };

        getQuotes();
    }, []);

    console.log('quotes test', quotes);

    return (
        <div>
            <h1>Hello StackBlitz!</h1>
            <p>Start editing to see some magic happen :)</p>
            <ul>
                {quotes.map((quote, idx) => <li key={quote.id}>{quote.quote}</li>)}
            </ul>
        </div>
    );
}
