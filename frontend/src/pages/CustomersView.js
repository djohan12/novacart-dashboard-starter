/**
 * CustomersView.js — Customer List page
 *
 * This page shows:
 *   - A sortable table of top 20 customers by revenue
 *   - Columns: Name | City | State | Orders | Total Spent
 *   - A date range filter
 *
 * The data fetching is already wired up.
 * Your job: implement the UI and the sorting logic.
 */

import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { getCustomers, getMinMaxDateRange} from '../utils/api';

function formatCurrency(value) {
  if (!value) return '$0';
  return `$${Number(value).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default function CustomersView() {
  const [startDate,  setStartDate]  = useState('2022-01-01');
  const [endDate,    setEndDate]    = useState('2022-12-31');
  const [customers,  setCustomers]  = useState([]);
  const [sortBy,     setSortBy]     = useState('total_spent');
  const [sortDir,    setSortDir]    = useState('desc');
  const [loading,    setLoading]    = useState(true);
  const [error,      setError]      = useState(null);
  const [minDate, setMinDate] = useState(null);
  const [maxDate, setMaxDate] = useState(null);

  useEffect(() => { loadData(); }, []);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const data = await getCustomers(startDate, endDate);
      const dateRange = await getMinMaxDateRange();
      setMinDate(dateRange["min_date"])
      setMaxDate(dateRange["max_date"])
      
      if (startDate > dateRange["max_date"] || endDate < dateRange["min_date"]) {
        setError(
          `Invalid date range. Please select dates between ${dateRange["min_date"]} and ${dateRange["max_date"]}.`
        );
        return;
      }

      if (startDate > endDate) {
        setError("Start date must be before or equal to end date.");
        return;
      }

      setCustomers(data);
    } catch (err) {
      if (err.message.includes('Failed to fetch') || err.message.includes('Load failed') ) {
        setError("The backend server is down. Please try again later.");
      } else {
        setError(err.message);
      }
      
    } finally {
      setLoading(false);
    }
  }

  // Sort handler — toggles direction if same column, resets to desc if new column
  function handleSort(column) {
    if (sortBy === column) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortDir('desc');
    }
  }

  // Apply sort to customers array
  const sorted = [...customers].sort((a, b) => {
    const va = a[sortBy], vb = b[sortBy];
    if (typeof va === 'number') return sortDir === 'asc' ? va - vb : vb - va;
    return sortDir === 'asc'
      ? String(va).localeCompare(String(vb))
      : String(vb).localeCompare(String(va));
  });

  // Sort indicator helper
  const sortIcon = (col) => sortBy === col ? (sortDir === 'asc' ? ' ↑' : ' ↓') : '';

  const tableStyles = {
    borderCollapse: 'collapse',
    fontSize: '18px',
  };  

  const leftAlignStyles = {
    textAlign: 'center',
    paddingBottom: '12px',
    paddingRight: '20px',
  };

  const tdStyles = {
    padding: '12px 24px',  // Changed from 16px to 24px
    borderBottom: '1px solid var(--border-color, #eee)',
  };


  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />
      <div className="page">

        <div className="filter-bar">
          <label>From</label>
          <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
          <label>To</label>
          <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
          <button className="btn-apply" onClick={loadData}>Apply</button>
          <span style={{ marginLeft: 'auto', fontSize: 13, color: 'var(--text-muted)' }}>
            {customers.length} customers
          </span>
        </div>

        {error && (
          <div style={{ color: '#C62828', padding: 16, background: '#FFEBEE', borderRadius: 8, marginBottom: 16 }}>
            Error: {error}
          </div>
        )}

        {loading && <div className="loading">Loading customers…</div>}

        {!loading && !error && (
          <div className="card">
            <div className="section-title" style={{ marginBottom: 16, fontSize: '20px'}}>
              Top Customers by Revenue
            </div>

            {/*
              STEP 1 — Sortable table
              sorted is: [{ customer_id, name, city, state, total_orders, total_spent }]

              Build a table with these columns:
                Name | City | State | Orders | Total Spent

              Each column header should be clickable and call handleSort(columnName).
              Use sortIcon(columnName) to show ↑ or ↓ on the active sort column.

              Hint: use a standard HTML <table> with <thead> and <tbody>.
              Style alternating rows with different background colors.
              Format total_spent with formatCurrency().
            */}

            <table>
              <thead>
                <tr style = {leftAlignStyles}>
                  <th style = {tableStyles} onClick={() => handleSort('name')}>Name{sortIcon('name')}</th>
                  <th style = {tableStyles} onClick={() => handleSort('city')}>City{sortIcon('city')}</th>
                  <th style = {tableStyles} onClick={() => handleSort('state')}>State{sortIcon('state')}</th>
                  <th style = {tableStyles} onClick={() => handleSort('total_orders')}>Orders{sortIcon('total_orders')}</th>
                  <th style = {tableStyles} onClick={() => handleSort('total_spent')}>Total Spent{sortIcon('total_spent')}</th>
                </tr>
              </thead>
              <tbody>
                {sorted.map((customer, index) => (
                  <tr key={customer.customer_id} style={{ backgroundColor: index % 2 === 0 ? 'var(--bg-secondary)' : 'var(--bg-primary)' }}>
                    <td style = {tdStyles}>{customer.name}</td>
                    <td style = {tdStyles}>{customer.city}</td>
                    <td style = {tdStyles}>{customer.state}</td>
                    <td style = {tdStyles}>{customer.total_orders}</td>
                    <td style = {tdStyles}>{formatCurrency(customer.total_spent)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
