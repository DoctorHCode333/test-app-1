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
      field: "phrases",
      header: "Phrases",
      filter: true,
      filterPlaceholder: "Search for a Phrase",
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
      field: "ANI",
      header: "ANI",
      filter: true,
      filterPlaceholder: "Search by ANI",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "authType",
      header: "Authentication Type",
      filter: true,
      filterPlaceholder: "Search by Authentication Type",
      className: "rounded-lg border divide-y divide-x",
      filterMenuStyle: { width: "14rem" },
      width: "150px",
    },
    {
      field: "partyId",
      header: "Party ID",
      filter: true,
      filterPlaceholder: "Search by Party ID",
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
    phrases: { value: null, matchMode: FilterMatchMode.CONTAINS },
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
    silence: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    other: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    ANI: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    authType: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
    partyId: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
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
       startDate: item["Start Date"],
      convId: item["Conversation ID"],
      phrases: item["Phrases"],

      lob: item["LOB"],
      marketType: item["Market Type"],
      division: item["Division"],
      queue: item["Queue"],
      clientId: item["Client ID"],
      workTeams: item["Work Teams"],
      agentId: item["Agent Name"],
      sScore: item["Sentiment Score"],
      sTrend: item["Sentiment Trend"],
      call: item["Call Duration"],
      agentDuration: item["Agent Duration"],
      acwTime: item["ACW Time"],
      callHandleTime: item["Call Handle Time"],   
      silence: item["Silence Time %"],
      other: item["Other(Hold/Noise/SP) Time %"],
      authType: item["Authentication Type"],
      ANI: item["ANI"],
      partyId: item["Party ID"],
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

//   const handleFilterChange = (e) => {
//     console.log(e);
//     console.log(e.filteredValue);
    
//   };

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


<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <groupId>longtime</groupId>
  <artifactId>automation</artifactId>
  <version>0.0.1-SNAPSHOT</version>
  <packaging>jar</packaging>

  <name>automation</name>
  <url>http://maven.apache.org</url>

  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.source>21</maven.compiler.source>
        <maven.compiler.target>21</maven.compiler.target>
        <maven.shade.plugin.version>3.2.1</maven.shade.plugin.version>
        <maven.compiler.plugin.version>3.6.1</maven.compiler.plugin.version>
        <exec-maven-plugin.version>1.6.0</exec-maven-plugin.version>
        <aws.java.sdk.version>2.18.16</aws.java.sdk.version>
        <slf4j.version>1.7.28</slf4j.version>
        <junit5.version>5.8.1</junit5.version>
  </properties>

  <dependencies>
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>3.8.1</version>
      <scope>test</scope>
    </dependency>
    
    <dependency>
    <groupId>com.opencsv</groupId>
    <artifactId>opencsv</artifactId>
    <version>4.1</version>
</dependency>

<dependency>
    <groupId>javax.mail</groupId>
    <artifactId>mail</artifactId>
    <version>1.5.0-b01</version>
</dependency>
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
            <version>${slf4j.version}</version>
        </dependency>
		<!-- https://mvnrepository.com/artifact/com.mysql/mysql-connector-j -->
<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
    <version>8.3.0</version>
</dependency>
		
         <!--<dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-simple</artifactId>
            <version>${slf4j.version}</version>
        </dependency>-->

        <!-- Needed to adapt Apache Commons Logging used by Apache HTTP Client to Slf4j to avoid
        ClassNotFoundException: org.apache.commons.logging.impl.LogFactoryImpl during runtime -->
        <dependency>
            <groupId>org.apache.logging.log4j</groupId>
            <artifactId>log4j-slf4j-impl</artifactId>
            <version>2.17.2</version>
        </dependency>

        <!-- Test Dependencies -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>${junit5.version}</version>
            <scope>test</scope>
        </dependency>

  <!-- https://mvnrepository.com/artifact/com.mypurecloud/platform-client-v2 -->
<dependency>
    <groupId>com.mypurecloud</groupId>
    <artifactId>platform-client-v2</artifactId>
    <version>171.0.0</version>
</dependency>
  
  <dependency>
        <groupId>org.seleniumhq.selenium</groupId>
        <artifactId>selenium-java</artifactId>
        <version>3.141.59</version>
    </dependency>
    
    <dependency>
    <groupId>commons-io</groupId>
    <artifactId>commons-io</artifactId>
    <version>2.15.1</version>
</dependency>
    
    <!-- https://mvnrepository.com/artifact/com.datastax.cassandra/cassandra-driver-core -->
<dependency>
    <groupId>com.datastax.cassandra</groupId>
    <artifactId>cassandra-driver-core</artifactId>
    <version>3.10.1</version>
</dependency>
    
<!-- https://mvnrepository.com/artifact/org.json/json -->
<dependency>
    <groupId>org.json</groupId>
    <artifactId>json</artifactId>
    <version>20220924</version>
</dependency>

  
	
    
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>3.8.1</version>
      <scope>test</scope>
    </dependency>
    <dependency>
    <groupId>com.amazonaws</groupId>
    <artifactId>aws-java-sdk</artifactId>
    <version>1.11.163</version>
</dependency>
 
 	


<dependency>
		<groupId>com.oracle</groupId>
		<artifactId>ojdbc</artifactId>
		<version>12.2.0.1</version>
		<scope>system</scope>
		<systemPath>C:\Harsh_official\Batch_Files\All_batch_Jobs\AutomationCopyHarsh - Copy\ojdbc7.jar</systemPath>
</dependency>
	
<dependency>
		<groupId>org.apache.httpcomponents.client5</groupId>
		<artifactId>httpclient5</artifactId>
		<version>5.1</version>
</dependency>

 
<dependency>
    <groupId>com.microsoft.sqlserver</groupId>
    <artifactId>mssql-jdbc</artifactId>
    <version>6.1.0.jre8</version>
</dependency>
   
 <dependency>
   <groupId>com.jcraft</groupId>
   <artifactId>jsch</artifactId>
   <version>0.1.42</version>
</dependency>

 <dependency>
   <groupId>org.apache.poi</groupId>
   <artifactId>poi-ooxml</artifactId>
   <version>5.2.5</version>
</dependency>
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-api</artifactId>
    <version>2.17.2</version>
</dependency>
<dependency>
    <groupId>org.apache.logging.log4j</groupId>
    <artifactId>log4j-core</artifactId>
    <version>2.17.2</version>
</dependency>

  </dependencies>
  <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>${maven.compiler.plugin.version}</version>
            </plugin>
        </plugins>
    </build>
</project>
