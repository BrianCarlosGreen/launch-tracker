"use client";

import { useEffect, useMemo, useState } from "react";

type Filters = {
  agencies: string[];
  states: string[];
  lv_types: string[];
  sites: string[];
};

type Launch = {
  launch_tag: string | null;
  launch_datetime_utc: string | null;
  launch_date_raw: string | null;
  launch_agency: string | null;
  lv_state: string | null;
  lv_type: string | null;
  launch_site: string | null;
  launch_code: string | null;
  name: string | null;
  plname: string | null;
};

type AttemptsByYear = {
  year: number;
  count: number;
};

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

function buildParams(params: Record<string, string | number | null>) {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== "") {
      searchParams.set(key, String(value));
    }
  });
  return searchParams.toString();
}

function AttemptsChart({ data }: { data: AttemptsByYear[] }) {
  if (!data.length) {
    return <div className="chart">No data yet.</div>;
  }
  const maxCount = Math.max(...data.map((entry) => entry.count));
  const width = 800;
  const height = 220;
  const padding = 24;
  const barWidth = (width - padding * 2) / data.length;

  return (
    <svg className="chart" viewBox={`0 0 ${width} ${height}`}>
      {data.map((entry, index) => {
        const barHeight = (entry.count / maxCount) * (height - padding * 2);
        const x = padding + index * barWidth;
        const y = height - padding - barHeight;
        return (
          <g key={entry.year}>
            <rect
              x={x + 2}
              y={y}
              width={barWidth - 4}
              height={barHeight}
              fill="#2563eb"
              rx={3}
            />
            {barWidth > 30 && (
              <text
                x={x + barWidth / 2}
                y={height - 6}
                fontSize="10"
                textAnchor="middle"
                fill="#52606d"
              >
                {entry.year}
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}

export default function DashboardPage() {
  const [filters, setFilters] = useState<Filters>({
    agencies: [],
    states: [],
    lv_types: [],
    sites: []
  });
  const [since, setSince] = useState("");
  const [until, setUntil] = useState("");
  const [agency, setAgency] = useState("");
  const [state, setState] = useState("");
  const [lvType, setLvType] = useState("");
  const [site, setSite] = useState("");
  const [attempts, setAttempts] = useState<number>(0);
  const [attemptsByYear, setAttemptsByYear] = useState<AttemptsByYear[]>([]);
  const [launches, setLaunches] = useState<Launch[]>([]);
  const [offset, setOffset] = useState(0);
  const limit = 20;

  const queryParams = useMemo(
    () => ({
      since,
      until,
      agency,
      state,
      lv_type: lvType,
      site
    }),
    [since, until, agency, state, lvType, site]
  );

  useEffect(() => {
    fetch(`${apiBase}/api/meta/filters`)
      .then((res) => res.json())
      .then((data) => setFilters(data))
      .catch(() => setFilters({ agencies: [], states: [], lv_types: [], sites: [] }));
  }, []);

  useEffect(() => {
    const params = buildParams(queryParams);
    fetch(`${apiBase}/api/stats/orbital_attempts?${params}`)
      .then((res) => res.json())
      .then((data) => setAttempts(data.count ?? 0))
      .catch(() => setAttempts(0));

    fetch(`${apiBase}/api/stats/attempts_by_year?${params}`)
      .then((res) => res.json())
      .then((data) => setAttemptsByYear(data))
      .catch(() => setAttemptsByYear([]));
  }, [queryParams]);

  useEffect(() => {
    setOffset(0);
  }, [since, until, agency, state, lvType, site]);

  useEffect(() => {
    const params = buildParams({ ...queryParams, limit, offset });
    fetch(`${apiBase}/api/launches?${params}`)
      .then((res) => res.json())
      .then((data) => setLaunches(data))
      .catch(() => setLaunches([]));
  }, [queryParams, offset]);

  const resetFilters = () => {
    setSince("");
    setUntil("");
    setAgency("");
    setState("");
    setLvType("");
    setSite("");
    setOffset(0);
  };

  return (
    <main>
      <h1>Orbital Launch Tracker</h1>
      <p>Canonical counts based on DISTINCT Launch_Tag values in the GCAT Orbital Launch Log.</p>

      <div className="grid grid-2" style={{ marginTop: 16 }}>
        <div className="card">
          <h2>Orbital launch attempts</h2>
          <div className="metric">{attempts.toLocaleString()}</div>
          <div className="badge">Filtered view</div>
        </div>
        <div className="card">
          <h2>Date range</h2>
          <div className="grid grid-2">
            <div>
              <label htmlFor="since">Since (inclusive)</label>
              <input
                id="since"
                type="date"
                value={since}
                onChange={(event) => {
                  setSince(event.target.value);
                  setOffset(0);
                }}
              />
            </div>
            <div>
              <label htmlFor="until">Until (exclusive)</label>
              <input
                id="until"
                type="date"
                value={until}
                onChange={(event) => {
                  setUntil(event.target.value);
                  setOffset(0);
                }}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h2>Filters</h2>
        <div className="grid grid-3">
          <div>
            <label>Agency</label>
            <select value={agency} onChange={(event) => setAgency(event.target.value)}>
              <option value="">All</option>
              {filters.agencies.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label>Launch state</label>
            <select value={state} onChange={(event) => setState(event.target.value)}>
              <option value="">All</option>
              {filters.states.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label>Launch vehicle type</label>
            <select value={lvType} onChange={(event) => setLvType(event.target.value)}>
              <option value="">All</option>
              {filters.lv_types.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label>Launch site</label>
            <select value={site} onChange={(event) => setSite(event.target.value)}>
              <option value="">All</option>
              {filters.sites.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </div>
          <div style={{ alignSelf: "end" }}>
            <button className="secondary" onClick={resetFilters}>
              Reset filters
            </button>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h2>Attempts per year</h2>
        <AttemptsChart data={attemptsByYear} />
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h2>Recent launches</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Launch tag</th>
              <th>Vehicle</th>
              <th>Agency</th>
              <th>Site</th>
              <th>State</th>
              <th>Name</th>
            </tr>
          </thead>
          <tbody>
            {launches.map((launch, index) => (
              <tr key={launch.launch_tag ?? `launch-${index}`}>
                <td>
                  {launch.launch_datetime_utc
                    ? new Date(launch.launch_datetime_utc).toISOString().slice(0, 10)
                    : launch.launch_date_raw ?? ""}
                </td>
                <td>{launch.launch_tag}</td>
                <td>{launch.lv_type}</td>
                <td>{launch.launch_agency}</td>
                <td>{launch.launch_site}</td>
                <td>{launch.lv_state}</td>
                <td>{launch.name || launch.plname}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="pagination">
          <button
            className="secondary"
            onClick={() => setOffset(Math.max(0, offset - limit))}
            disabled={offset === 0}
          >
            Previous
          </button>
          <span>
            Showing {offset + 1} - {offset + launches.length}
          </span>
          <button
            className="secondary"
            onClick={() => setOffset(offset + limit)}
            disabled={launches.length < limit}
          >
            Next
          </button>
        </div>
      </div>
    </main>
  );
}
