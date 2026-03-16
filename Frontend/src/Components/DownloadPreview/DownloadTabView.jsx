import React, { useState, useEffect } from 'react';
import { TabView, TabPanel } from 'primereact/tabview';
import SummaryPage from './SummaryPage';
import TopicsPage from './TopicsPage';
import "./customTab.css";

const DownloadTabView = (props) => {
    const [scrollableTabs, setScrollableTabs] = useState([]);
    const { finalGroupData,summaryData,downloadData,setDownloadData,selectedDownloadOptions } = props;
    const temparray=[]
//    downloadData.map((item)=>item.name.includes('Aubrey')?temparray.push(item.name):"");
  //console.log(summaryData,downloadData)
    
useEffect(() => {
    setScrollableTabs([]);
    // Prepare the tabs in one go
    if (
      selectedDownloadOptions.length == 1 &&
      selectedDownloadOptions.includes("Summary")
    ) {
      setScrollableTabs((prevData) => [
        ...prevData,
        { title: "Summary", content: <SummaryPage data={summaryData} /> },
      ]);
    } else {
      if (
        selectedDownloadOptions.includes("All") ||
        selectedDownloadOptions.includes("Summary")
      ) {
        setScrollableTabs((prevData) => [
          ...prevData,
          { title: "Summary", content: <SummaryPage data={summaryData} /> },
        ]);
      }
      finalGroupData.map((item) => {
        setScrollableTabs((prevData) => [
          ...prevData,
          {
            title: item.name,
            content: (
              <TopicsPage
                downloadData={downloadData}
                data={item.data}
                setDownloadData={setDownloadData}
              />
            ),
          },
        ]);
      });
    }
  }, [finalGroupData, summaryData]); // Trigger whenever finalGroupData changes

    return (
        <div className='card' >
               <TabView
                key={scrollableTabs.length}
               scrollable>
                   {scrollableTabs.map((tab,index) => {
                       return (
                         
                           
                           <TabPanel key={index} header={tab.title} >
                               <hr />
                               <br/>
                               {tab.content}
                           </TabPanel>
                          
                       );
                   })}
               </TabView>
           </div>
    );
};

export default DownloadTabView;
// import React, { useState } from 'react';
// import { TabView, TabPanel } from 'primereact/tabview';
// import SummaryPage from './SummaryPage';
// import TopicsPage from './TopicsPage';
// import { useEffect } from 'react';

// const DownloadTabView = (props) =>{
//     const [scrollableTabs, setScrollableTabs ] = useState([])
//     const {downloadData} = props
//     let propsData = downloadData.downloadData;
//     console.log(downloadData.summaryData, propsData, 'inisde tab view download', scrollableTabs)
//    useEffect(() => {
//     if (Object.keys(downloadData).length !== 0) {
//     setScrollableTabs((prevData) => [...prevData,  {title : 'Summary', content: <SummaryPage data={downloadData.summaryData}/>}])
//     setScrollableTabs((prevData) => [...prevData,  {title : 'Positive Feedback', content: <TopicsPage data={propsData.positiveFeedback}/>}])
//     setScrollableTabs((prevData) => [...prevData,  {title : 'Negative Feedback', content: <TopicsPage data={propsData.negativeFeedback}/>}])
//     // propsData.map((item) =>{
//     //     setScrollableTabs((prevData) => [...prevData, {title: item.name, content: <TopicsPage data={item.data} />}])
//     // })
//     }
//    }, [])

    
//     // const scrollableTabs = Array.from({ length: 50 }, (_, i) => ({ title: `Tab ${i + 1}`, content: `Tab ${i + 1} Content` }))
// {/* <button className='px-10 py-2 bg-gray-300 hover:bg-gray-300 text-gray-700 font-semibold rounded-md'>{tab.title}</button> */}
//     return (
//         <div className='card' >
//             <TabView scrollable>
//                 {scrollableTabs.map((tab) => {
//                     return (
//                         <TabPanel key={tab.title} header={tab.title} >
//                             <hr/>
//                             <br/>
//                             <p className="m-0">{tab.content}</p>
//                         </TabPanel>
//                     );
//                 })}
//             </TabView>
//         </div>

//     )
// }


// export default DownloadTabView;
        