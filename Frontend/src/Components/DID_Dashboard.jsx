import React, { useEffect, useState, useMemo } from "react";
import { useSelector, useDispatch } from "react-redux";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { InputText } from "primereact/inputtext";
import { Dropdown } from "primereact/dropdown";
import { Tag } from "primereact/tag";
import { ProgressSpinner } from "primereact/progressspinner";
import { Button } from "primereact/button";
import { getAllDIDs } from "../utils/genesysCloudApi";
import { setDIDData, setDIDLoading, setDIDError } from "../Redux/actions";
import Nav from "./Nav";

const DID_Dashboard = () => {
  const dispatch = useDispatch();
  const didData = useSelector((state) => state.didData);
  const didLoading = useSelector((state) => state.didLoading);
  const didError = useSelector((state) => state.didError);

  const [globalFilter, setGlobalFilter] = useState("");
  const [assignmentFilter, setAssignmentFilter] = useState(null);

  const assignmentOptions = [
    { label: "All", value: null },
    { label: "Assigned", value: "assigned" },
    { label: "Unassigned", value: "unassigned" },
  ];

  useEffect(() => {
    fetchDIDData();
  }, []);

  const fetchDIDData = async () => {
    dispatch(setDIDLoading(true));
    dispatch(setDIDError(null));
    try {
      const data = await getAllDIDs();
      dispatch(setDIDData(data));
    } catch (err) {
      dispatch(setDIDError(err.message || "Failed to fetch DIDs"));
    } finally {
      dispatch(setDIDLoading(false));
    }
  };

  // Calculate statistics
  const stats = useMemo(() => {
    if (!didData || didData.length === 0) {
      return { total: 0, assigned: 0, unassigned: 0 };
    }
    const unassigned = didData.filter(
      (did) => did.isUnassigned || (!did.owner && !did.ownerType)
    ).length;
    return {
      total: didData.length,
      assigned: didData.length - unassigned,
      unassigned: unassigned,
    };
  }, [didData]);

  // Filter data based on assignment status
  const filteredData = useMemo(() => {
    if (!didData) return [];
    let filtered = [...didData];

    if (assignmentFilter === "assigned") {
      filtered = filtered.filter((did) => !did.isUnassigned && (did.owner || did.ownerType));
    } else if (assignmentFilter === "unassigned") {
      filtered = filtered.filter((did) => did.isUnassigned || (!did.owner && !did.ownerType));
    }

    return filtered;
  }, [didData, assignmentFilter]);

  // Template for assignment status column
  const assignmentBodyTemplate = (rowData) => {
    const isAssigned = !rowData.isUnassigned && (rowData.owner || rowData.ownerType);
    return (
      <span
        className={`px-3 py-1.5 rounded-full text-xs font-semibold tracking-wide ${
          isAssigned
            ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
            : "bg-amber-500/20 text-amber-400 border border-amber-500/30"
        }`}
      >
        {isAssigned ? "Assigned" : "Unassigned"}
      </span>
    );
  };

  // Template for phone number column
  const phoneNumberTemplate = (rowData) => {
    return (
      <span className="font-mono font-semibold text-cyan-400">
        {rowData.phoneNumber || rowData.number || "N/A"}
      </span>
    );
  };

  // Template for owner column
  const ownerTemplate = (rowData) => {
    if (rowData.owner) {
      return (
        <span className="text-slate-200">
          {rowData.owner.name || rowData.owner.id || "Unknown"}
        </span>
      );
    }
    return <span className="text-slate-500 italic">--</span>;
  };

  // Template for owner type column
  const ownerTypeTemplate = (rowData) => {
    if (rowData.ownerType) {
      return (
        <span className="px-2.5 py-1 rounded-md text-xs font-medium bg-blue-500/20 text-blue-400 border border-blue-500/30">
          {rowData.ownerType}
        </span>
      );
    }
    return <span className="text-slate-500 italic">--</span>;
  };

  // Template for state column
  const stateTemplate = (rowData) => {
    return (
      <span className="text-slate-300 capitalize">
        {rowData.state || "--"}
      </span>
    );
  };

  // Template for DID Pool column
  const didPoolTemplate = (rowData) => {
    if (rowData.didPool?.name) {
      return (
        <span className="text-purple-400 font-medium">
          {rowData.didPool.name}
        </span>
      );
    }
    return <span className="text-slate-500 italic">--</span>;
  };

  // Header with search and filter
  const renderHeader = () => {
    return (
      <div className="flex flex-wrap gap-4 justify-between items-center py-2">
        <div className="flex gap-3 items-center">
          <div className="relative">
            <i className="pi pi-search absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <InputText
              value={globalFilter}
              onChange={(e) => setGlobalFilter(e.target.value)}
              placeholder="Search DIDs..."
              className="pl-10 w-72 bg-slate-800/50 border-slate-600 text-slate-200 placeholder-slate-400 rounded-lg focus:border-cyan-500 focus:ring-cyan-500/20"
            />
          </div>
        </div>
        <div className="flex gap-3 items-center">
          <Dropdown
            value={assignmentFilter}
            options={assignmentOptions}
            onChange={(e) => setAssignmentFilter(e.value)}
            placeholder="Filter by Status"
            className="w-48 bg-slate-800/50 border-slate-600"
          />
          <Button
            icon="pi pi-refresh"
            label="Refresh"
            onClick={fetchDIDData}
            className="bg-gradient-to-r from-cyan-600 to-blue-600 border-0 hover:from-cyan-500 hover:to-blue-500 shadow-lg shadow-cyan-500/20 px-5 py-2.5"
            loading={didLoading}
          />
        </div>
      </div>
    );
  };

  if (didLoading && (!didData || didData.length === 0)) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <Nav />
        <div className="flex flex-col items-center justify-center h-96">
          <ProgressSpinner strokeWidth="3" className="text-cyan-500" />
          <p className="mt-4 text-slate-400 text-lg">Loading DIDs...</p>
        </div>
      </div>
    );
  }

  if (didError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <Nav />
        <div className="flex flex-col items-center justify-center h-96">
          <div className="bg-red-500/20 p-6 rounded-full mb-4">
            <i className="pi pi-exclamation-triangle text-5xl text-red-400"></i>
          </div>
          <p className="text-red-400 text-lg mb-4">{didError}</p>
          <Button
            label="Retry"
            icon="pi pi-refresh"
            onClick={fetchDIDData}
            className="bg-gradient-to-r from-cyan-600 to-blue-600 border-0"
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <Nav />
      <div className="px-8 py-8">
        {/* Statistics Cards - Centered with max width */}
        <div className="flex justify-center mb-10">
          <div className="grid grid-cols-3 gap-6">
            {/* Total DIDs Card */}
            <div className="relative overflow-hidden bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur-xl rounded-2xl border border-slate-700/50 p-8 shadow-xl hover:shadow-2xl hover:shadow-cyan-500/10 transition-all duration-300 group min-w-[280px]">
              <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="relative flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">
                    Total DIDs
                  </p>
                  <p className="text-5xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                    {stats.total}
                  </p>
                </div>
                <div className="bg-gradient-to-br from-cyan-500/20 to-blue-500/20 p-4 rounded-xl border border-cyan-500/30">
                <i className="pi pi-phone text-3xl text-cyan-400"></i>
              </div>
            </div>
          </div>

          {/* Assigned Card */}
          <div className="relative overflow-hidden bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur-xl rounded-2xl border border-slate-700/50 p-8 shadow-xl hover:shadow-2xl hover:shadow-emerald-500/10 transition-all duration-300 group min-w-[280px]">
            <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="relative flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">
                  Assigned
                </p>
                <p className="text-5xl font-bold bg-gradient-to-r from-emerald-400 to-green-400 bg-clip-text text-transparent">
                  {stats.assigned}
                </p>
              </div>
              <div className="bg-gradient-to-br from-emerald-500/20 to-green-500/20 p-4 rounded-xl border border-emerald-500/30">
                <i className="pi pi-check-circle text-3xl text-emerald-400"></i>
              </div>
            </div>
          </div>

          {/* Unassigned Card */}
          <div className="relative overflow-hidden bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur-xl rounded-2xl border border-slate-700/50 p-8 shadow-xl hover:shadow-2xl hover:shadow-amber-500/10 transition-all duration-300 group min-w-[280px]">
            <div className="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="relative flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-2">
                  Unassigned
                </p>
                <p className="text-5xl font-bold bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">
                  {stats.unassigned}
                </p>
              </div>
              <div className="bg-gradient-to-br from-amber-500/20 to-orange-500/20 p-4 rounded-xl border border-amber-500/30">
                <i className="pi pi-exclamation-circle text-3xl text-amber-400"></i>
              </div>
            </div>
          </div>
        </div>
        </div>

        {/* DID Table */}
        <div className="bg-gradient-to-br from-slate-800/60 to-slate-900/60 backdrop-blur-xl rounded-2xl border border-slate-700/50 shadow-2xl overflow-hidden">
          <DataTable
            value={filteredData}
            paginator
            rows={15}
            rowsPerPageOptions={[10, 15, 25, 50]}
            dataKey="id"
            globalFilter={globalFilter}
            header={renderHeader()}
            emptyMessage={
              <div className="text-center py-8 text-slate-400">
                <i className="pi pi-inbox text-4xl mb-3 block"></i>
                No DIDs found.
              </div>
            }
            className="p-datatable-dark"
            stripedRows
            responsiveLayout="scroll"
            loading={didLoading}
            style={{ background: "transparent" }}
          >
            <Column
              field="phoneNumber"
              header="Phone Number"
              body={phoneNumberTemplate}
              sortable
              style={{ minWidth: "160px" }}
            />
            <Column
              field="name"
              header="Name"
              sortable
              style={{ minWidth: "150px" }}
              body={(rowData) => (
                <span className="text-slate-200">{rowData.name || "--"}</span>
              )}
            />
            <Column
              header="Status"
              body={assignmentBodyTemplate}
              sortable
              style={{ minWidth: "130px" }}
            />
            <Column
              header="Owner"
              body={ownerTemplate}
              sortable
              style={{ minWidth: "150px" }}
            />
            <Column
              header="Owner Type"
              body={ownerTypeTemplate}
              sortable
              style={{ minWidth: "130px" }}
            />
            <Column
              field="state"
              header="State"
              body={stateTemplate}
              sortable
              style={{ minWidth: "100px" }}
            />
            <Column
              field="didPool.name"
              header="DID Pool"
              body={didPoolTemplate}
              sortable
              style={{ minWidth: "150px" }}
            />
          </DataTable>
        </div>
      </div>
    </div>
  );
};

export default DID_Dashboard;