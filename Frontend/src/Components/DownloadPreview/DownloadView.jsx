import React, { useState, useRef, useEffect } from "react";
import { Button } from "primereact/button";
import { Dialog } from "primereact/dialog";
import Loading from "../Loading_Download_Preview";
import * as XLSX from "xlsx";
import { Toast } from "primereact/toast";
import { MultiSelect } from "primereact/multiselect";
import DownloadTabView from "./DownloadTabView";
import {
  getGroupDownloadData,
  getInteractionsTrendDownloadData,
} from "../../API/TopicAPI";
import { useSelector } from "react-redux";
// import { setDownloadData } from "../../Redux/actions";

const DownloadView = (props) => {
  const [visible, setVisible] = useState(false);
  const {
    filters,
    dateRange,
    groupNames,
    selectedGroup,
    tab,
    setDownloadData,
    selectedCallDuration,
    selectedACDTime,
    selectedCustomerTime,
    selectedAgentTime,
    selectedSilenceTime,
    selectedIVRTime,
    selectedOthersTime,
    selectedOvertalkCount,
  } = props;

  const downloadData = useSelector((state) => state.fetchDownloadData);
  const [loading, setLoading] = useState(false);
  const [finalData, setFinalData] = useState([]);
  const [finalDataHolder, setFinalDataHolder] = useState([]);
  const [summaryData, setSummaryData] = useState([]);
  const [selectedDownloadOptions, setSelectedDownloadOptions] = useState([
    "All",
  ]);
  const [sortedDownloadOptions, setSortedDownloadOptions] = useState([]);
  const [downloadOptions, setDownloadOptions] = useState([
    { label: "All", value: "All" },
    { label: "Summary", value: "Summary" },
    { label: "Positive Feedback", value: "Positive Feedback" },
    { label: "Negative Feedback", value: "Negative Feedback" },
  ]);

  const selectedDownloadData = useRef(downloadData);

  useEffect(() => {
    selectedDownloadData.current = downloadData;
    // console.log("hello", selectedDownloadData.current);
  }, [downloadData]);

  useEffect(() => {
    // const temp = downloadOptions.sort((a, b) => {
    //   const aSelected = selectedDownloadOptions.some((item) => item === a.label);
    //   const bSelected = selectedDownloadOptions.some((item) => item === b.label);
    //   return aSelected === bSelected ? 0 : aSelected ? -1 : 1;
    // });

    setSortedDownloadOptions(downloadOptions);
  }, [downloadOptions]);

  const toast = useRef(null);
  const isCancelledRef = useRef(false); // Reference for cancellation

  const showDownloadErrorToast = () => {
    toast.current.show({
      severity: "error",
      summary: "Download Failed",
      detail: "An error occurred during the download. Please try again.",
      life: 3000,
    });
  };

  // Function to hide dialog and stop loading
  const hideDialog = () => {
    //console.log("Hide111");
    setSelectedDownloadOptions(["All"]);
    setVisible(false);
    isCancelledRef.current = true; // Set the cancel flag
  };

  const handleDownload = async () => {
    // Check date range validity
    if (!dateRange.startDate || !dateRange.endDate) {
      toast.current.show({
        severity: "error",
        summary: "Invalid Date Range",
        detail: "Please select a valid date range.",
      });
      return;
    }

    setVisible(true); // Show the dialog
    setLoading(true);
    setFinalData([]);
    setFinalDataHolder([]);
    setSelectedDownloadOptions(["All"]);
    isCancelledRef.current = false; // Reset cancellation flag

    try {
      // Check if the dialog was closed before proceeding with the fetch
      if (isCancelledRef.current) {
        setVisible(false);
        return;
      }

      //  const interactionsTrendDataResponse = await getInteractionsTrendDownloadData({
      //         startDate: dateRange.startDate,
      //         endDate: dateRange.endDate,
      //         selectedCallDuration: selectedCallDuration,
      //         selectedACDTime: selectedACDTime,
      //         selectedCustomerTime: selectedCustomerTime,
      //         selectedAgentTime: selectedAgentTime,
      //         selectedSilenceTime: selectedSilenceTime,
      //         selectedIVRTime: selectedIVRTime,
      //         selectedOthersTime: selectedOthersTime,
      //         selectedOvertalkCount: selectedOvertalkCount,
      //         lob: filters.lob,
      //         marketSector:  filters.marketSector,
      //         queue:  filters.queue,
      //         clientId:  filters.clientId,
      //         agentId:  filters.agentId,
      //         ANI:  filters.ANI,
      //       });

      const interactionsTrendDownloadDataResponse =
        await getInteractionsTrendDownloadData({
          startDate: dateRange.startDate,
          endDate: dateRange.endDate,
          selectedCallDuration: selectedCallDuration,
          selectedACDTime: selectedACDTime,
          selectedCustomerTime: selectedCustomerTime,
          selectedAgentTime: selectedAgentTime,
          selectedSilenceTime: selectedSilenceTime,
          selectedIVRTime: selectedIVRTime,
          selectedOthersTime: selectedOthersTime,
          selectedOvertalkCount: selectedOvertalkCount,
          lob: filters.selectedLOB,
          marketSector: filters.selectedMarketSector,
          division: filters.selectedDivision,
          queue: filters.selectedQueue,
          clientId: filters.selectedClientId,
          workTeams: filters.selectedWorkTeams,
          agentId: filters.selectedAgentId,
          ANI: filters.selectedANI,
          callDuration: filters.selectedCallDuration,
          agentDuration: filters.selectedAgentDuration,
          acwTime: filters.selectedAcwTime,
          callHandleTime: filters.selectedCallHandleTime,
        });

      const groupNamesData = groupNames.slice(0, 100);

      const tempOptions = [
        { label: "All", value: "All" },
        { label: "Summary", value: "Summary" },
      ];
      groupNamesData.map((name) => {
        tempOptions.push({ label: name, value: name });
      });
      setDownloadOptions(tempOptions);

      const apiCalls1 = groupNamesData.map(async (item) => {
        let responseAllData;

        responseAllData = await getGroupDownloadData({
          startDate: dateRange.startDate,
          endDate: dateRange.endDate,
          selectedCallDuration: selectedCallDuration,
          selectedACDTime: selectedACDTime,
          selectedCustomerTime: selectedCustomerTime,
          selectedAgentTime: selectedAgentTime,
          selectedSilenceTime: selectedSilenceTime,
          selectedIVRTime: selectedIVRTime,
          selectedOthersTime: selectedOthersTime,
          selectedOvertalkCount: selectedOvertalkCount,
          lob: filters.selectedLOB,
          marketSector: filters.selectedMarketSector,
          division: filters.selectedDivision,
          queue: filters.selectedQueue,
          clientId: filters.selectedClientId,
          workTeams: filters.selectedWorkTeams,
          agentId: filters.selectedAgentId,
          ANI: filters.selectedANI,
          callDuration: filters.selectedCallDuration,
          agentDuration: filters.selectedAgentDuration,
          acwTime: filters.selectedAcwTime,
          callHandleTime: filters.selectedCallHandleTime,
          group: selectedGroup,
          groupName: item,
          tab: tab,
        });

        const finalResponse = {
          name: item,
          data: responseAllData.data ? responseAllData.data : [],
        };

        return finalResponse;
        // console.log(
        //   responseAllData,
        //   "Dowwnload all phrtases data api response --tahnks",
        //   item
        // );
      });

      Promise.all(apiCalls1)
        .then((result) => {
          //console.log(result);

          setFinalData(result);
          setFinalDataHolder(result);
        })
        .finally(() => {
          setLoading(false);
        });

      // Update download data if fetch is not cancelled
      if (!isCancelledRef.current) {
        //console.log(interactionsTrendDownloadDataResponse);

        setSummaryData(interactionsTrendDownloadDataResponse.summaryData);
      } else {
        setVisible(false);
        setLoading(true); // Ensure loading stops if cancelled
      }
    } catch (error) {
      console.log(error);

      setVisible(false);
      setLoading(true); // Stop loading on error
      //console.log("Error while fetching download Data", error);
      showDownloadErrorToast();
    }
  };

  const generateExcel = (selectedOptions, summaryData, finalData) => {
    try {
      const wb = XLSX.utils.book_new();
      const summarySheet = XLSX.utils.json_to_sheet(summaryData);
      // console.log(selectedDownloadData.current);

      // const groupData = XLSX.utils.json_to_sheet(finalData);

      if (selectedOptions.includes("All")) {
        XLSX.utils.book_append_sheet(wb, summarySheet, "Summary");
        console.log(finalData);
        
        finalData.map((finalItem, finalIndex) => {
          const details = finalItem.data.map((item) => {
            let transformedData = {};
            if (selectedDownloadData.current.length === 0) {
              transformedData = { ...item };
            } else {
              console.log("Entered Here", selectedDownloadData.current);
              selectedDownloadData.current.forEach((header) => {
                transformedData[header] = item[header];
              });
            }
            transformedData["Conversation ID"] = {
              v: item["Conversation ID"],
              l: {
                Target: `https://apps.usw2.pure.cloud/directory/#/engage/admin/interactions/${item["Conversation ID"]}`,
                Tooltip: "Click to see conversation",
              },
            };
            console.log(transformedData);
            
            return transformedData;
          });
          const detailsSheet = XLSX.utils.json_to_sheet(details);
          let finalName;
          if (finalItem.name.length > 30) {
            finalName = selectedGroup + "_" + finalIndex;``
          } else {
            finalName = finalItem.name;
          }
          XLSX.utils.book_append_sheet(wb, detailsSheet, finalName);
        });
      } else {
        if (selectedOptions.includes("Summary")) {
          XLSX.utils.book_append_sheet(wb, summarySheet, "Summary");
        }

        finalData.map((finalItem, finalIndex) => {
          if (selectedDownloadOptions.includes(finalItem.name)) {
            const details = finalItem.data.map((item) => {
              let transformedData = {};
              if (selectedDownloadData.current.length == 0) {
                transformedData = { ...item };
              } else {
                selectedDownloadData.current.forEach((header) => {
                  transformedData[header] = item[header];
                });
              }
              transformedData["Conversation ID"] = {
                v: item["Conversation ID"],
                l: {
                  Target: `https://apps.usw2.pure.cloud/directory/#/engage/admin/interactions/${item["Conversation ID"]}`,
                  Tooltip: "Click to see conversation",
                },
              };
              return transformedData;
            });
            const detailsSheet = XLSX.utils.json_to_sheet(details);
            let finalName;
            if (finalItem.name.length > 30) {
              finalName = selectedGroup + "_" + finalIndex;
            } else {
              finalName = finalItem.name;
            }
            XLSX.utils.book_append_sheet(wb, detailsSheet, finalName);
          }
        });
      }

      const fileName = `Acoustic_Data_${selectedGroup}_${dateRange.startDate}_to_${dateRange.endDate}.xlsx`;
      XLSX.writeFile(wb, fileName);
    } catch (error) {
      console.log(error);

      showDownloadErrorToast();
    }
  };

  const downloadExcelData = () => {
    if (selectedDownloadOptions.length === 0) {
      showDownloadErrorToast();
      return;
    } else {
      generateExcel(selectedDownloadOptions, summaryData, finalData);
    }
  };

  const handleApply = () => {
    if (
      selectedDownloadOptions.length == 1 &&
      selectedDownloadOptions.includes("Summary")
    ) {
      console.log(selectedDownloadOptions);

      setFinalData([]);
    } else {
      if (
        selectedDownloadOptions.includes("All") ||
        selectedDownloadOptions.length == 0
      ) {
        setSelectedDownloadOptions(["All"]);
        setFinalData(finalDataHolder);
      } else {
        setFinalData(
          finalDataHolder.filter((item) =>
            selectedDownloadOptions.includes(item.name)
          )
        );
      }
    }
  };

  return (
    <div>
      <div className="card" style={{ maxWidth: "200px" }}>
        <Toast ref={toast} />
        <Button
          label="Download Preview"
          className="ml-3 mt-2 bg-blue-950 border mb-2 mr-2 text-white text-xs font-semibold py-3 px-8 rounded-lg"
          // icon="pi pi-download"
          onClick={handleDownload}
        />

        <Dialog
          header={`${tab}  Data Download Preview`}
          className="custom-dialog bg-gradient-to-tl from-orange-400 via-amber-400 to-orange-400 pt-10 rounded-xl"
          visible={visible}
          maximizable
          style={{ width: "80%" }}
          onHide={hideDialog}
        >
          {loading ? (
            <Loading />
          ) : (
            <>
              <p className="mb-4">
                You can download the below {tab} data from{" "}
                <b>
                  {dateRange.startDate} to {dateRange.endDate}
                </b>{" "}
                as Excel format.
              </p>
              <div className="flex justify-start items-center text-xs mb-2 mt-4">
                <MultiSelect
                  value={selectedDownloadOptions}
                  onChange={(e) => setSelectedDownloadOptions(e.value)}
                  options={sortedDownloadOptions}
                  optionLabel="label"
                  filter
                  placeholder="Select File"
                  maxSelectedLabels={3}
                  className="w-full mb-1 border md:w-60"
                  virtualScrollerOptions={{
                    itemSize: 24,
                  }}
                />
                <Button
                  label="Apply"
                  className="ml-3 bg-blue-950 border mb-2 mr-2 text-white text-xs font-semibold py-3 px-8 rounded-lg"
                  onClick={handleApply}
                />
                <Button
                  label="Download"
                  className="ml-3 bg-blue-950 border mb-2 mr-2 text-white text-xs font-semibold py-3 px-8 rounded-lg"
                  onClick={downloadExcelData}
                />
              </div>
              <hr />
              <DownloadTabView
               selectedDownloadOptions={selectedDownloadOptions}
                setDownloadData={setDownloadData}
                downloadData={downloadData}
                finalGroupData={finalData}
                summaryData={summaryData}
              />
            </>
          )}
        </Dialog>
      </div>
    </div>
  );
};

export default DownloadView;
