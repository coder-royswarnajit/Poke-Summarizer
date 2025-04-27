import React, { useState, useEffect } from 'react';
import { Wallet, ArrowDownCircle, ArrowUpCircle, Plus, DollarSign } from 'lucide-react';

const WalletDashboard = () => {
  // This would be connected to actual wallet data in production
  const [walletInfo, setWalletInfo] = useState({
    address: "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    balance: 0.025,
    currency: "ETH",
    network: "Base"
  });
  
  const [transactions, setTransactions] = useState([
    { 
      hash: "0x8a7d...f932", 
      type: "deposit", 
      amount: 0.01, 
      date: "2025-04-25", 
      status: "confirmed" 
    },
    { 
      hash: "0x3c9a...e721", 
      type: "payment", 
      amount: 0.01, 
      date: "2025-04-25", 
      status: "confirmed" 
    }
  ]);

  return (
    <div className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow-md">
      <div className="flex items-center mb-4">
        <Wallet className="w-6 h-6 mr-2 text-blue-600" />
        <h2 className="text-xl font-bold text-gray-800 dark:text-gray-200">Base Wallet</h2>
      </div>
      
      <div className="mb-6 bg-gray-100 dark:bg-gray-700 p-3 rounded-md">
        <div className="text-sm text-gray-500 dark:text-gray-400">Wallet Address</div>
        <div className="flex items-center space-x-2">
          <div className="font-mono text-sm truncate">
            {walletInfo.address}
          </div>
          <button className="text-blue-600 hover:text-blue-800 text-xs">
            Copy
          </button>
        </div>
      </div>
      
      <div className="flex mb-6">
        <div className="flex-1 text-center p-3 bg-blue-50 dark:bg-blue-900 rounded-l-lg">
          <div className="text-sm text-gray-500 dark:text-gray-400">Balance</div>
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {walletInfo.balance} {walletInfo.currency}
          </div>
          <div className="text-xs mt-1">on {walletInfo.network}</div>
        </div>
        <div className="flex-1 flex flex-col justify-around p-3 bg-gray-50 dark:bg-gray-700 rounded-r-lg space-y-2">
          <button className="flex items-center justify-center text-sm bg-green-500 text-white p-1 rounded hover:bg-green-600">
            <Plus size={16} className="mr-1" /> Add Funds
          </button>
          <button className="flex items-center justify-center text-sm bg-blue-500 text-white p-1 rounded hover:bg-blue-600">
            <DollarSign size={16} className="mr-1" /> Pay
          </button>
        </div>
      </div>
      
      <div>
        <h3 className="text-md font-semibold mb-2 text-gray-700 dark:text-gray-300">Recent Transactions</h3>
        <div className="space-y-2">
          {transactions.map((tx, index) => (
            <div key={index} className="p-2 border border-gray-200 dark:border-gray-700 rounded flex items-center">
              {tx.type === "deposit" ? (
                <ArrowDownCircle size={16} className="text-green-500 mr-2" />
              ) : (
                <ArrowUpCircle size={16} className="text-blue-500 mr-2" />
              )}
              <div className="flex-1">
                <div className="flex justify-between">
                  <span className="text-sm font-medium">{tx.type === "deposit" ? "Received" : "Payment"}</span>
                  <span className="text-sm font-bold">
                    {tx.type === "deposit" ? "+" : "-"}{tx.amount} {walletInfo.currency}
                  </span>
                </div>
                <div className="flex justify-between text-xs text-gray-500">
                  <span>{tx.date}</span>
                  <span>{tx.status}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WalletDashboard;