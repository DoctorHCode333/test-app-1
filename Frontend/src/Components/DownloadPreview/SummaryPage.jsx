import React, { useState, useEffect } from "react";
import { Button } from "primereact/button";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
// import { CustomerService } from './service/CustomerService';
// import { fetchConversations } from "../../../utils/genesysApi";
// import { InputText } from "primereact/inputtext";
// import { IconField } from "primereact/iconfield";

const SummaryPage = (props) => {

  const [customers, setCustomers] = useState(
    props.data.map((item) => {
      const customer = {
        header: item.Header,
        count: item.Count,
        past: item["Past Count"],
        trend: item.Trend + "%"
      };
      return customer;
    })
  );


  return (
    <div className="card rounded-xl">
      <DataTable
        value={customers}
        scrollable  
        scrollHeight='70vh'
        showGridlines
        paginator
        rows={5}
        rowsPerPageOptions={[5, 10, 25, 50, 100, 500, 1000]}
        tableStyle={{ minWidth: "50rem" }}
        className="rounded-lg border divide-y divide-x"
        paginatorTemplate="RowsPerPageDropdown FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink"
        currentPageReportTemplate="{first} to {last} of {totalRecords}"
      >
        <Column
          field="header"
          header="Header"
          style={{ minWidth: "21rem" }}
          className="rounded-lg border divide-y divide-x"
        ></Column>
        {/* <Column field="lob" header="LOB" style={{ minWidth: '14rem' }} className="rounded-lg border divide-y divide-x"></Column> */}
        <Column
          field="count"
          header="Interaction Count"
          style={{ minWidth: "14rem" }}
          className="rounded-lg border divide-y divide-x"
        ></Column>
        <Column
          field="past"
          header="Past Count"
          style={{ minWidth: "14rem" }}
          className="rounded-lg border divide-y divide-x"
        ></Column>
        <Column
          field="trend"
          header="Trend"
          style={{ minWidth: "14rem" }}
          className="rounded-lg border divide-y divide-x"
        ></Column>

        {/* <Column field="queue" header="Device Type" filter filterPlaceholder="Search by Queue" filterMenuStyle={{ width: '14rem' }} style={{ minWidth: '14rem' }} className="rounded-lg border divide-y divide-x"></Column>
                <Column field="clientId" header="Interaction Reason" filter filterPlaceholder="Search by Client ID" filterMenuStyle={{ width: '14rem' }} style={{ minWidth: '14rem' }} className="rounded-lg border divide-y divide-x"></Column> */}
        {/* <Column field="marketType" header="Comments" filter filterPlaceholder="Search by MarketType" filterMenuStyle={{ width: '14rem' }} style={{ minWidth: '14rem' }} className="rounded-lg border divide-y divide-x"></Column> */}
      </DataTable>
    </div>
  );
};

export default SummaryPage;

// import React, { useState, useEffect } from 'react';
// import { Button } from 'primereact/button';
// import { DataTable } from 'primereact/datatable';
// import { Column } from 'primereact/column';
// // import { CustomerService } from './service/CustomerService';
// // import { fetchConversations } from "../../../utils/genesysApi";
// import { InputText } from 'primereact/inputtext';
// import { IconField } from 'primereact/iconfield';

// const SummaryPage = (props) => {
//     // const [customers, setCustomers] = useState([{
//     //     id: 1000,
//     //     name: 'James Butt',
//     //     country: {
//     //         name: 'Algeria',
//     //         code: 'dz'
//     //     },
//     //     company: 'Benton, John B Jr',
//     //     date: '2015-09-13',
//     //     status: 'unqualified',
//     //     verified: true,
//     //     activity: 17,
//     //     representative: {
//     //         name: 'Ioni Bowcher',
//     //         image: 'ionibowcher.png'
//     //     },
//     //     balance: 70663
//     // }]);
//     //console.log("hihihihihidata",props.data);
//          let global =  [
//             {
//               header: 'Total Feedback',
//               count: 1649,
//               past: 1286,
//               trend: 28.23,
//               ratio: 1.98
//             },
//             {
//               header: 'Total Feedback',
//               count: 1649,
//               past: 1286,
//               trend: 28.23,
//               ratio: 1.98
//             },
//             {
//               header: 'Total Feedback',
//               count: 1649,
//               past: 1286,
//               trend: 28.23,
//               ratio: 1.98
//             }
//           ]

//         //   const global = props.data.map((item) => (
//         //     {

//         //       header: item.Header,

//         //       // sentimentScore: Math.round(item[9]*100),
//         //       count:  item.Count,
//         //       past:  item["Past Count"],
//         //       trend:  item.Trend +"%",
//         //       ratio:  item["PF/NF Ratio"]+(item.Header=='Total Feedback'?" +Ve/-Ve Feedback":"%"),

//         //     }
//         // ))
//           const [customers, setCustomers] = useState(global)

// //  const transformData = (data) => {

// //         // setCustomers(props.data.map((item) => (

// //         //     {name: item[0], count: item[1], percentage: item[2].toFixed(2), lob: item[3]}
// //         // )))
// //         const result = {}
// //         data.map((item) => {
// //             if(!result[item[0]]){

// //                 result[item[0]] = {
// //                     topicName: item[0],
// //                     // countWS: 0, percentWS: 0,
// //                     // countWO: 0, percentWO: 0,
// //                     // countEB: 0, percentEB: 0,
// //                     // countHO: 0, percentHO: 0

// //                 }
// //             }

// //             switch(item[3]) {
// //                 case 'WS':
// //                   result[item[0]].countWS = item[1];
// //                   result[item[0]].percentWS = item[2].toFixed(2);
// //                   break;
// //                 case 'WO':
// //                   result[item[0]].countWO = item[1];
// //                   result[item[0]].percentWO = item[2].toFixed(2);
// //                   break;
// //                 case 'EB':
// //                   result[item[0]].countEB = item[1];
// //                   result[item[0]].percentEB = item[2].toFixed(2);
// //                   break;
// //                 case 'HO':
// //                   result[item[0]].countHO = item[1];
// //                   result[item[0]].percentHO = item[2].toFixed(2);
// //                   break;
// //                 default:
// //                   break;
// //               }
// //         });
// //         return Object.values(result)

// //  }
// //  const onConvIdChange = (e) => {
// //   const value = e.target.value;
// //   const input=String(value);

// //   //let response = fetchConversations(input);
// //   console.log(response);

// // };
// //  const renderHeader = () => {
// //   return (
// //       <div className="flex justify-content-end">
// //           <IconField iconPosition="left">
// //               {/* <InputIcon className="pi pi-search" /> */}
// //               <InputText className='border px-4 py-3'  onChange={(e)=>setInputValue(e.target.value)} onKeyDown={onConvIdChange} placeholder=" Search" />
// //           </IconField>
// //       </div>
// //   );
// // };

//  //const transformedData = transformData(props.data);
//  //console.log(transformedData, 'transformed data')
// //  const header = renderHeader();
//     // const paginatorLeft = <Button type="button" icon="pi pi-refresh" text />;
//     // const paginatorRight = <Button type="button" icon="pi pi-download" text />;

//     // useEffect(() => {
//     //     CustomerService.getCustomersMedium().then((data) => setCustomers(data));
//     // }, []);
//     // paginatorLeft={paginatorLeft} paginatorRight={paginatorRight}
//     return (
//         <div className="card">
//             <DataTable value={customers} showGridlines  paginator rows={5} rowsPerPageOptions={[5, 10, 25, 50, 100, 500, 1000]} tableStyle={{ minWidth: '50rem' }} className="rounded-lg border divide-y divide-x"
//                     paginatorTemplate="RowsPerPageDropdown FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink"
//                     currentPageReportTemplate="{first} to {last} of {totalRecords}" > {/*header={header} */}
//                 <Column field="header" header="Header" style={{ minWidth: '21rem' }} className="rounded-lg border divide-y divide-x"></Column>
//                 {/* <Column field="neg" header="LOB" filter filterPlaceholder="Search by LOB" filterMenuStyle={{ width: '14rem' }} style={{ minWidth: '14rem' }} className="rounded-lg border divide-y divide-x"></Column> */}
//                 <Column field="count" header="Interaction Count" style={{ minWidth: '14rem' }} className="rounded-lg border divide-y divide-x"></Column>
//                 <Column field="past" header="Past Count" style={{ minWidth: '14rem' }} className="rounded-lg border divide-y divide-x"></Column>
//                 <Column field="trend" header="Trend in %" style={{ minWidth: '14rem' }} className="rounded-lg border divide-y divide-x"></Column>
//                 <Column field="ratio" header="PF/NF Ratio" style={{ minWidth: '14rem' }} className="rounded-lg border divide-y divide-x"></Column>

//                 {/* <Column field="queue" header="Device Type" filter filterPlaceholder="Search by Queue" filterMenuStyle={{ width: '14rem' }} style={{ minWidth: '14rem' }} className="rounded-lg border divide-y divide-x"></Column>
//                 <Column field="clientId" header="Interaction Reason" filter filterPlaceholder="Search by Client ID" filterMenuStyle={{ width: '14rem' }} style={{ minWidth: '14rem' }} className="rounded-lg border divide-y divide-x"></Column> */}
//                 {/* <Column field="marketType" header="Comments" filter filterPlaceholder="Search by MarketType" filterMenuStyle={{ width: '14rem' }} style={{ minWidth: '14rem' }} className="rounded-lg border divide-y divide-x"></Column> */}
//             </DataTable>
//         </div>
//     );
// }

// export default SummaryPage;
