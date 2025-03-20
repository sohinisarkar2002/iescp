function initCharts(
  activeUsers,
  publicCampaigns,
  privateCampaigns,
  adRequestStatuses,
  flaggedUsers,
  flaggedCampaigns
) {
  // Active users chart
  var ctxUser = document.getElementById("userChart").getContext("2d");
  new Chart(ctxUser, {
    type: "bar",
    data: {
      labels: ["Active Users"],
      datasets: [
        {
          label: "Active Users",
          data: [activeUsers || 0],
          backgroundColor: "rgba(249, 105, 14, 0.5)",
          borderColor: "rgba(241, 90, 34, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
        },
      },
      plugins: {
        legend: {
          display: true,
          labels: {
            color: "rgba(0, 0, 0, 1)",
          },
        },
      },
    },
  });

  // Campaigns chart (public/private)
  var ctxCampaign = document.getElementById("campaignChart").getContext("2d");
  new Chart(ctxCampaign, {
    type: "bar",
    data: {
      labels: ["Campaigns"],
      datasets: [
        {
          label: "Public Campaigns",
          data: [publicCampaigns || 0],
          backgroundColor: "rgba(54, 162, 235, 0.4)",
          borderColor: "rgba(54, 162, 235, 1)",
          borderWidth: 1,
        },
        {
          label: "Private Campaigns",
          data: [privateCampaigns || 0],
          backgroundColor: "rgba(153, 102, 255, 0.6)",
          borderColor: "rgba(153, 102, 255, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
        },
      },
      plugins: {
        legend: {
          display: true,
          labels: {
            color: "rgba(0, 0, 0, 1)",
          },
        },
      },
    },
  });

  // Ad requests chart (status - pending, accepted, rejected)
  var ctxAdRequest = document.getElementById("adRequestChart").getContext("2d");
  new Chart(ctxAdRequest, {
    type: "bar",
    data: {
      labels: ["Ad Requests"],
      datasets: [
        {
          label: "Pending",
          data: [adRequestStatuses.values[0]],
          backgroundColor: "rgba(255, 255, 0, 0.5)",
          borderColor: "rgba(255, 255, 0, 1)",
          borderWidth: 1,
        },
        {
          label: "Accepted",
          data: [adRequestStatuses.values[1]],
          backgroundColor: "rgba(0, 255, 0, 0.5)",
          borderColor: "rgba(0, 255, 0, 1)",
          borderWidth: 1,
        },
        {
          label: "Rejected",
          data: [adRequestStatuses.values[2]],
          backgroundColor: "rgba(255, 0, 0, 0.6)",
          borderColor: "rgba(255, 0, 0, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
        },
      },
      plugins: {
        legend: {
          display: true,
          labels: {
            color: "rgba(0, 0, 0, 1)",
          },
        },
      },
    },
  });

  // Flagged chart (users/ampaigns)
  var ctxFlagged = document.getElementById("flaggedChart").getContext("2d");
  new Chart(ctxFlagged, {
    type: "bar",
    data: {
      labels: ["Flagged"],
      datasets: [
        {
          label: "Flagged Users",
          data: [flaggedUsers || 0],
          backgroundColor: "rgba(75, 192, 75, 0.6)",
          borderColor: "rgba(75, 192, 75, 1)",
          borderWidth: 1,
        },
        {
          label: "Flagged Campaigns",
          data: [flaggedCampaigns || 0],
          backgroundColor: "rgba(128, 0, 32, 0.6)",
          borderColor: "rgba(128, 0, 32, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
        },
      },
      plugins: {
        legend: {
          display: true,
          labels: {
            color: "rgba(0, 0, 0, 1)",
          },
        },
      },
    },
  });
}
