// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

// Pie Chart Example
var ctx = document.getElementById("myPieChart");
var still = document.getElementById("covid-still").value;
var death = document.getElementById("covid-death").value;
var recovered = document.getElementById("covid-recovered").value;
var myPieChart = new Chart(ctx, {
  type: 'doughnut',
  data: {
    datasets: [{
      data: [still, recovered, death],
      backgroundColor: ['#36b9cc', '#1cc88a', '#E74A3B'],
      hoverBackgroundColor: ['#2c9faf', '#17a673', '#E74A3B'],
      hoverBorderColor: "rgba(234, 236, 244, 1)",
    }],
    labels: ["Sick %", "recovered %", "death %"]
  },
  options: {
    maintainAspectRatio: false,
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      caretPadding: 10,
    },
    legend: {
      display: false
    },
    cutoutPercentage: 80,
  },
});
