/**
 * ProductsView.js — Product Performance page
 *
 * This page shows:
 *   - A bar chart of top 10 products by revenue
 *   - A table with product name, category, units sold, and revenue
 *   - A date range filter
 *
 * The data fetching is already wired up.
 * Your job: implement the UI.
 */

import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import Navbar from '../components/Navbar';
import { getProducts, getMinMaxDateRange } from '../utils/api';

// Format currency helper
function formatCurrency(value) {
  if (!value) return '$0';
  if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
  if (value >= 1000)    return `$${(value / 1000).toFixed(0)}K`;
  return `$${value.toFixed(2)}`;
}

export default function ProductsView() {
  const [startDate, setStartDate] = useState('2022-01-01');
  const [endDate,   setEndDate]   = useState('2022-12-31');
  const [products,  setProducts]  = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState(null);
  const [minDate, setMinDate] = useState(null);
  const [maxDate, setMaxDate] = useState(null);

  useEffect(() => { loadData(); }, []);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const data = await getProducts(startDate, endDate);
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

      setProducts(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />
      <div className="page">

        <div className="filter-bar">
          <label>From</label>
          <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} min = {minDate} max = {maxDate} />
          <label>To</label>
          <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} min = {minDate} max = {maxDate} />
          <button className="btn-apply" onClick={loadData}>Apply</button>
        </div>

        {error && (
          <div style={{ color: '#C62828', padding: 16, background: '#FFEBEE', borderRadius: 8, marginBottom: 16 }}>
            Error: {error}
          </div>
        )}

        {loading && <div className="loading">Loading products data…</div>}

        {!loading && !error && (
          <div className="grid-2">

            {/*
              STEP 1 — Top products bar chart
              products is: [{ product_id, name, category, units_sold, revenue }]
              Use a horizontal BarChart (layout="vertical").
              XAxis type="number", YAxis type="category" dataKey="name"
              Hint: truncate long product names to 20 chars
            */}
            <div className="card">
              <div className="section-title" style={{ marginBottom: 16 }}>Top 10 Products by Revenue</div>
              {/* TODO: add your bar chart here */}
              <ResponsiveContainer width="100%" height={450}>
                  <BarChart layout="vertical" data={products}>
                    <XAxis type="number" />
                    <YAxis type="category" dataKey="name" width={200} tickFormatter={(value) => value.length > 25 ? value.substring(0, 20) + '...' : value}/>
                    <Tooltip formatter={(value) => formatCurrency(value)} />
                    <Bar dataKey="revenue" fill="#8884d8" />
                  </BarChart>
              </ResponsiveContainer>
            </div>

            {/*
              STEP 2 — Products table
              Show all products in a table: Name | Category | Units Sold | Revenue
              Hint: use an HTML table or build with divs.
              Format revenue with the formatCurrency helper above.
            */}
            <div className="card">
              <div className="section-title" style={{ marginBottom: 16 }}>Product Details</div>
              {/* TODO: add your table here */}
                <table style={{width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '2px solid #ccc' }}>
                    <th style={{ textAlign: 'left', padding: 12, fontWeight: 600 }}>Name</th>
                    <th style={{ textAlign: 'left', padding: 12, fontWeight: 600 }}>Category</th>
                    <th style={{ textAlign: 'right', padding: 12, fontWeight: 600 }}>Units Sold</th>
                    <th style={{ textAlign: 'right', padding: 12, fontWeight: 600 }}>Revenue</th>
                    </tr>
                    </thead>
              <tbody>
                {products.map((product) => (
                <tr key={product.product_id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: 12 }}>{product.name}</td>
                <td style={{ padding: 12 }}>{product.category}</td>
                <td style={{ textAlign: 'right', padding: 12 }}>{product.units_sold}</td>
                <td style={{ textAlign: 'right', padding: 12 }}>{formatCurrency(product.revenue)}</td>
                </tr>
              ))}
              </tbody>
              </table>
            </div>

          </div>
        )}
      </div>
    </div>
  );
}
