function initSponsorCharts(
  totalCampaigns,
  activeCampaigns,
  expiredCampaigns,
  upcomingCampaigns,
  adRequestLabels,
  adRequestValues
) {
  // Campaigns chart
  var ctxCampaigns = document.getElementById("campaignsChart").getContext("2d");
  new Chart(ctxCampaigns, {
    type: "pie",
    data: {
      labels: ["Active Campaigns", "Expired Campaigns", "Upcoming Campaigns"],
      datasets: [
        {
          label: "# of Campaigns",
          data: [activeCampaigns, expiredCampaigns, upcomingCampaigns],
          backgroundColor: [
            "rgba(0, 200, 0, 0.7)",   // Active
            "rgba(255, 0, 0, 0.8)",    // Expired
            "rgba(0, 0, 200, 0.7)",   // Upcoming
          ],
          borderColor: [
            "rgba(0, 200, 0, 1)",     // Active
            "rgba(255, 0, 0, 1)",      // Expired
            "rgba(0, 0, 200, 1)"     // Upcoming
          ],
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "top",
        },
        tooltip: {
          callbacks: {
            label: function (tooltipItem) {
              return tooltipItem.label + ": " + tooltipItem.raw;
            },
          },
        },
        datalabels: {
          display: true,
          color: "white",
          anchor: "end",
          align: "top",
          formatter: (value) => `${value}`,
        },
      },
      aspectRatio: 1,
    },
  });

  // Ad requests chart
  const filteredLabels = adRequestLabels.filter(
    (label) => label !== "Negotiating"
  );
  const filteredValues = adRequestValues.filter(
    (value, index) => adRequestLabels[index] !== "Negotiating"
  );

  var ctxAdRequests = document
    .getElementById("adRequestsChart")
    .getContext("2d");
  new Chart(ctxAdRequests, {
    type: "pie",
    data: {
      labels: filteredLabels,
      datasets: [
        {
          label: "# of Ad Requests",
          data: filteredValues,
          backgroundColor: [
            "rgba(255, 159, 64, 0.8)", // Pending
            "rgba(0, 128, 0, 0.8)", // Accepted
            "rgba(255, 67, 54, 0.8)", // Rejected
          ],
          borderColor: [
            "rgba(255, 159, 64, 1)", // Pending
            "rgba(0, 128, 0, 1)", // Accepted
            "rgba(255, 67, 54, 1)", // Rejected
          ],
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "top",
        },
        tooltip: {
          callbacks: {
            label: function (tooltipItem) {
              return tooltipItem.label + ": " + tooltipItem.raw;
            },
          },
        },
        datalabels: {
          display: true,
          color: "white",
          anchor: "end",
          align: "top",
          formatter: (value) => `${value}`,
        },
      },
      aspectRatio: 1, 
    },
  });

  
  console.log("Campaigns Chart Data:", {
    labels: ["Active Campaigns", "Expired Campaigns", "Upcoming Campaigns"],
    datasets: [
      {
        data: [activeCampaigns, expiredCampaigns, upcomingCampaigns],
      },
    ],
  });

  console.log("Ad Requests Chart Data:", {
    labels: filteredLabels,
    datasets: [
      {
        data: filteredValues,
      },
    ],
  });
}
