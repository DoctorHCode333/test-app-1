import React, { useState, useEffect } from "react";
import { Button } from "primereact/button";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { FilterMatchMode, FilterOperator } from "primereact/api";
import { MultiSelect } from "primereact/multiselect";

// import {setDownloadData} from '../../Redux/actions'

const TopicsPage = (props) => {
  const { downloadData, setDownloadData } = props;
  const [selectedColumnNames, setSelectedColumnNames] = useState([]);

  const columns = [
    {
      field: "convId",
      header: "Conversation ID",
      filter: true,
      filterPlaceholder: "Search by ID",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { minWidth: "14rem" },
      width: "150px",
    },
    {
      field: "startDate",
      header: "Start Date",
      sortable: true,
      filter: true,
      filterPlaceholder: "Search by Start Date",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "lob",
      header: "LOB",
      filter: true,
      filterPlaceholder: "Search by LOB",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { minWidth: "14rem" },
      width: "150px",
    },
    {
      field: "marketType",
      header: "Market Type",
      filter: true,
      filterPlaceholder: "Search by Market Type",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "division",
      header: "Division",
      filter: true,
      filterPlaceholder: "Search by Divison",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "queue",
      header: "Queue",
      filter: true,
      filterPlaceholder: "Search by Queue",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "clientId",
      header: "Client ID",
      filter: true,
      filterPlaceholder: "Search by Client ID",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "workTeams",
      header: "Work Teams",
      filter: true,
      filterPlaceholder: "Search by Work Teams",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "agentId",
      header: "Agent Name",
      filter: true,
      filterPlaceholder: "Search by Agent Name",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "sScore",
      header: "Sentiment Score",
      sortable: true,
      filter: true,
      filterPlaceholder: "Search by Sentiment Score",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "sTrend",
      header: "Sentiment Trend",
      sortable: true,
      filter: true,
      filterPlaceholder: "Search by Sentiment Trend",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "call",
      header: "Call Duration",
      sortable: true,
      filter: true,
      filterPlaceholder: "Search by Call Duration(minutes)",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "agentDuration",
      header: "Agent Duration",
      sortable: true,
      filter: true,
      filterPlaceholder: "Search by Agent Duration(minutes)",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "acwTime",
      header: "ACW Time",
      sortable: true,
      filter: true,
      filterPlaceholder: "Search by ACW Time(seconds)",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "callHandleTime",
      header: "Call Handle Time",
      sortable: true,
      filter: true,
      filterPlaceholder: "Search by Call Handle Time(seconds)",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "IVR",
      header: "IVR Time %",
      sortable: true,
      filter: true,
      filterPlaceholder: "Search by IVR %",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "queueTime",
      header: "Queue Wait Time %",
      sortable: true,
      filter: true,
      filterPlaceholder: "Search by Queue Wait %",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "agent",
      header: "Agent Talk Time %",
      sortable: true,
      filter: true,
      filterPlaceholder: "Search by Agent Talk %",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "customer",
      header: "Customer Talk Time %",
      sortable: true,
      filter: true,
      filterPlaceholder: "Search by Cutomer Talk %",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "silence",
      header: "Silence Time %",
      sortable: true,
      filter: true,
      filterPlaceholder: "Search by Silence Talk %",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "other",
      header: "Other(Hold/Noise/SP) Time %",
      sortable: true,
      filter: true,
      filterPlaceholder: "Search by Other Talk %",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "overtalk",
      header: "Overtalk %",
      sortable: true,
      filter: true,
      filterPlaceholder: "Search by Overtalk %",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "overtalkCount",
      header: "Overtalk Count",
      sortable: true,
      filter: true,
      filterPlaceholder: "Search by Overtalk Count",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "ANI",
      header: "ANI",
      filter: true,
      filterPlaceholder: "Search by ANI",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
  ];

  const [visibleColumns, setVisibleColumns] = useState(columns);

  useEffect(() => {
    //console.log("Change",selectedColumnNames,downloadData)
    setDownloadData(selectedColumnNames);
  }, [selectedColumnNames]);

  const onColumnToggle = (event) => {
    let selectedColumns = event.value;
    let orderedSelectedColumns = columns.filter((col) =>
      selectedColumns.some((sCol) => sCol.field === col.field)
    );
    setSelectedColumnNames(orderedSelectedColumns.map((item) => item.header));

    setVisibleColumns(orderedSelectedColumns);
  };

  const [filters, setFilters] = useState({
    convId: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    startDate: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    lob: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    marketType: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    division: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    queue: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    clientId: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    workTeams: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    agentId: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    sScore: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    sTrend: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    call: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    agentDuration: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    acwTime: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    callHandleTime: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    customer: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    agent: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    silence: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    IVR: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    queueTime: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    overtalk: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    other: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    overtalkCount: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    ANI: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
  });

  const [selectedCell, setSelectedCell] = useState(null);
  const [metaKey, setMetaKey] = useState(true);

  //convert UTC time to normal time
  const convertTime = (utcString) => {
    let utcDate = new Date(utcString);

    let localTimeString = utcDate.toLocaleString();
    return localTimeString;
  };

  const [customers, setCustomers] = useState(
    props.data.map((item) => ({
      convId: item["Conversation ID"],
      startDate: item["Start Date"],
      lob: item["LOB"],
      marketType: item["Market Type"],
      division: item["Division"],
      queue: item["Queue"],
      clientId: item["Client ID"],
      workTeams: item["Work Teams"],
      agentId: item["Agent Name"],
      sScore: item["Sentiment Score"],
      sTrend: item["Sentiment Trend"],
      call: item["Call Duration(minutes)"],
      agentDuration: item["Agent Duration(minutes)"],
      acwTime: item["ACW Time(seconds)"],
      callHandleTime: item["Call Handle Time(seconds)"],
      customer: item["Customer Talk Time %"],
      agent: item["Agent Talk Time %"],
      silence: item["Silence Time %"],
      IVR: item["IVR Time %"],
      queueTime: item["Queue Wait Time %"],
      overtalk: item["Overtalk %"],
      other: item["Other(Hold/Noise/SP) Time %"],
      overtalkCount: item["Overtalk Count"],
      ANI: item["ANI"],
    }))
  );

  // useEffect(() => {
  //     console.log(customers);
  //   }, [customers])

  const handleCellSelection = (e) => {
    setSelectedCell(e.value);
    let selectedData = e.value;

    if (selectedData.field === "convId") {
      console.log(selectedData?.rowData?.convId, "cell value");
      let convid = selectedData?.rowData?.convId;
      let url =
        "https://apps.usw2.pure.cloud/directory/#/engage/admin/interactions/" +
        convid;
      window.open(url, "_blank");
    }
  };

  const header = (
    <>
      <span className="text-sm  ml-3">Manage the columns in the table</span>

      <MultiSelect
        value={visibleColumns}
        options={columns}
        optionLabel="header"
        onChange={onColumnToggle}
        className="border w-full sm:w-20rem"
        display="chip"
        selectAllLabel="Select All Columns"
      />
    </>
  );

  const handleFilterChange = (e) => {
    console.log(e);
    console.log(e.filteredValue);
    
  };

  return (
    <div className="card">
      <DataTable
        filterDisplay="row"
        paginator
        showGridlines
        rows={5}
        rowsPerPageOptions={[5, 10, 25, 50, 100, 500, 1000]}
        scrollable
        value={customers}
        scrollHeight="60vh"
        header={header}
        tableStyle={{ minWidth: "50rem" }}
        className=" border  divide-y divide-x"
        paginatorTemplate="RowsPerPageDropdown FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink"
        currentPageReportTemplate="{first} to {last} of {totalRecords}"
        cellSelection
        selectionMode="single"
        onSelectionChange={handleCellSelection}
        metaKeySelection={metaKey}
        dataKey="id"
        filters={filters}
        onFilter={handleFilterChange}
      >
        {visibleColumns.map((col) => (
          <Column
            key={col.field}
            field={col.field}
            header={col.header}
            sortable={col.sortable}
            filter
            filterPlaceholder={col.filterPlaceholder}
            className={col.className}
            filterMenuStyle={col.filterMenuStyle}
            style={{ minWidth: col.width }}

          />
        ))}
      </DataTable>
    </div>
  );
};
export default TopicsPage;


import React, { useState } from 'react';
import { Button } from 'primereact/button';
import { ProgressSpinner } from 'primereact/progressspinner';
import { Card } from 'primereact/card';

const WordCloudViewer = () => {
  const [imageSrc, setImageSrc] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchWordCloud = async () => {
    setLoading(true);
    setImageSrc(null); // clear old image
    try {
      const response = await fetch('http://localhost:5000/api/wordcloud');
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setImageSrc(url);
    } catch (err) {
      console.error('Error fetching word cloud:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gradient-to-br from-gray-50 to-blue-100">
      <Card className="w-full max-w-3xl shadow-2xl p-6">
        <h2 className="text-2xl font-bold text-center mb-6 text-blue-800">Word Cloud Generator</h2>

        <div className="flex justify-center mb-6">
          <Button
            label="Generate Word Cloud"
            icon="pi pi-cloud"
            className="p-button-lg p-button-primary"
            onClick={fetchWordCloud}
          />
        </div>

        {loading && (
          <div className="flex justify-center items-center h-64">
            <ProgressSpinner style={{ width: '50px', height: '50px' }} strokeWidth="4" />
          </div>
        )}

        {imageSrc && (
          <div className="flex flex-col items-center">
            <img
              src={imageSrc}
              alt="Word Cloud"
              className="rounded-lg shadow-lg max-w-full h-auto transition duration-300 ease-in-out"
            />

            <a
              href={imageSrc}
              download="wordcloud.png"
              className="mt-4"
            >
              <Button
                icon="pi pi-download"
                label="Download Word Cloud"
                className="p-button-outlined p-button-success"
              />
            </a>
          </div>
        )}
      </Card>
    </div>
  );
};

export default WordCloudViewer;

