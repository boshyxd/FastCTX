import React, { useState } from 'react';

interface ButtonProps {
    label: string;
    onClick: () => void;
    variant?: 'primary' | 'secondary';
}

export const Button: React.FC<ButtonProps> = ({ label, onClick, variant = 'primary' }) => {
    return (
        <button 
            className={`btn btn-${variant}`}
            onClick={onClick}
        >
            {label}
        </button>
    );
};

export const Counter: React.FC = () => {
    const [count, setCount] = useState(0);
    
    const increment = () => setCount(count + 1);
    const decrement = () => setCount(count - 1);
    
    return (
        <div className="counter">
            <h2>Count: {count}</h2>
            <Button label="+" onClick={increment} />
            <Button label="-" onClick={decrement} variant="secondary" />
        </div>
    );
};

export default function HelloWorld() {
    return (
        <div className="hello-world">
            <h1>Hello World Component</h1>
            <Counter />
        </div>
    );
}