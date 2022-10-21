import Chart from "chart.js";
import moment from "moment";
import * as api from "./api";

const pdfVersion = "1.0";

pdfMake.fonts = {
  PublicSans: {
    normal: "PublicSans-Regular.ttf",
    bold: "PublicSans-Bold.ttf",
  },
  IBMPlexMono: {
    normal: "IBMPlexMono-Text.ttf",
    bold: "IBMPlexMono-Bold.ttf",
  },
};

const primaryBlue = "#003463";
const white = "#FFFFFF";

const defaultPdfStyle = {
  font: "PublicSans",
  fontSize: 8,
};

const pdfStyles = {
  header: {
    font: "IBMPlexMono",
    fontSize: 22,
  },
  subheader: {
    font: "IBMPlexMono",
    fontSize: 18,
  },
  boldContent: {
    bold: true,
  },
  center: {
    alignment: "center",
  },
};

const pdfHeader = {
  style: "section",
  table: {
    widths: ["2%", "83%", "15%"],
    body: [
      [
        {
          text: "    ",
          lineHeight: 1.5,
          fillColor: primaryBlue,
        },
        {
          text: "    ",
          lineHeight: 1.5,
          fillColor: primaryBlue,
        },
        {
          text: "      ",
          fillColor: primaryBlue,
          lineHeight: 1.5,
        },
      ],
      [
        {
          text: "    ",
          lineHeight: 2,
          fillColor: primaryBlue,
        },
        {
          text: "  Inverse Transparenz",
          style: "header",
          lineHeight: 2,
          fillColor: primaryBlue,
          color: white,
        },
        {
          text: `Version ${pdfVersion}`,
          fillColor: primaryBlue,
          color: white,
          lineHeight: 2,
        },
      ],
    ],
  },
  layout: "noBorders",
  lineHeight: 2,
};

const tableHeaderContent = {
  user_rid: "Verantwortlich",
  tool: "Tool",
  access_kind: "Art",
  justification: "Begründung",
  data_types: "Datentypen",
  timestamp: "Zeitstempel",
};

const chartDefaultTicks = {
  fontSize: 24,
  fontColor: "black",
  fontFamily: "IBMPlexMono, monospace",
};

const chartConfig = {
  type: "line",
  options: {
    scales: {
      xAxes: [
        {
          gridLines: {
            drawOnChartArea: false,
          },
          ticks: chartDefaultTicks,
        },
      ],
      yAxes: [
        {
          gridLines: {
            drawOnChartArea: false,
          },
          ticks: {
            ...chartDefaultTicks,
            beginAtZero: true,
            stepSize: 1,
          },
        },
      ],
    },
    legend: {
      display: false,
    },
    animation: {
      duration: 0.1,
    },
  },
};

const chartDatasetConfig = {
  borderColor: "black",
  borderWidth: 3,
  fill: "false",
};

class PdfGenerator {
  /**
   * Set the parameters with which this PDF is being generated.
   */
  setPdfData(ownerRid, userRid, minTimestamp, maxTimestamp) {
    this.ownerRid = ownerRid;
    this.userRid = userRid;
    this.minTimestamp = minTimestamp;
    this.maxTimestamp = maxTimestamp;
  }

  /**
   * Fetch data accesses from Overseer and generate a PDF.
   * @param {String} ownerRid The owner for whom the PDF is generated.
   * @param {String} userRid The data user that the report is generated on.
   * @param {String} minTimestamp The earliest date to include, formatted as YYYY-MM-DD.
   * @param {String} maxTimestamp The latest date to include, formatted as YYYY-MM-DD.
   */
  async loadAndGenerate(ownerRid, userRid, minTimestamp, maxTimestamp) {
    this.setPdfData(ownerRid, userRid, minTimestamp, maxTimestamp);
    this.documentContent = { content: [pdfHeader], styles: pdfStyles, defaultStyle: defaultPdfStyle };

    const data = await api.get(`data-accesses?date_start=${minTimestamp}&date_end=${maxTimestamp}`);
    this.accesses = data.accesses
      .filter((element) => element.user_rid === userRid)
      .map((access) => {
        return { ...access, timestamp: moment.utc(access.timestamp) }; // convert timestamp string to moment as utc
      });
    this.accesses.sort((left, right) => left.timestamp.diff(right.timestamp));

    let accessesPerDay = {};
    for (let m = moment(minTimestamp); m.diff(maxTimestamp, "days") <= 0; m.add(1, "days")) {
      accessesPerDay[m.format("DD.MM.YY")] = 0;
    }
    this.accesses.forEach((access) => (accessesPerDay[access.timestamp.format("DD.MM.YY")] += 1));

    // -- Generate the chart -- //

    // The chart needs to be added to the DOM to be generated correctly.
    this.chartElement = document.createElement("canvas");
    this.chartElement.setAttribute("id", "exportChart");
    document.body.appendChild(this.chartElement);

    const labelList = Object.keys(accessesPerDay);
    const dataList = Object.values(accessesPerDay);
    const lineChart = this.createChart(labelList, dataList);

    // Chart creation takes some time, so we await it here before continuing.
    await new Promise((resolve) => (lineChart.options.animation.onComplete = resolve));
    this.chartImage = lineChart.toBase64Image();
    this.chartElement.remove();

    // -- Create the PDF -- //

    this.addDocumentHeader();
    if (this.accesses.length > 0) {
      this.addGraph();
      this.addAccessesTable();
    } else {
      this.documentContent.content.push({
        text: "Im angegebenen Zeitraum wurden keine Datenzugriffe erfasst.",
        lineHeight: 1.5,
      });
    }
    window.createPdf(this.documentContent).open({}, window);
  }

  /**
   * Create a Chart object with the given data.
   * @param {[String]} labels chart labels
   * @param {[*]} data chart data
   * @returns complete Chart object to be rendered in HTML
   */
  createChart(labels, data) {
    let ctx = this.chartElement.getContext("2d");
    const lineChart = new Chart(ctx, {
      ...chartConfig,
      data: { labels: labels, datasets: [{ ...chartDatasetConfig, data: data }] },
    });
    return lineChart;
  }

  // -- Functions to add data to the generated PDF -- //

  /**
   * Add the document info header to the PDF.
   */
  addDocumentHeader() {
    const start = moment(this.minTimestamp).format("DD.MM.YYYY");
    const end = moment(this.maxTimestamp).format("DD.MM.YYYY");
    const headers = [
      { text: " ", lineHeight: 1.5 },
      { text: `Erstellt für: ${this.ownerRid}`, lineHeight: 1.5 },
      { text: `Abgedeckter Zeitraum: ${start}–${end}`, lineHeight: 1.5 },
      { text: `Datennutzer*in: ${this.userRid}`, lineHeight: 1.5 },
      { text: " ", lineHeight: 1 },
    ];
    this.documentContent.content.push(...headers);
  }

  /**
   * Add graph (converted to image) to the PDF.
   */
  addGraph() {
    this.documentContent.content.push({ text: "Überblick", style: "subheader", lineHeight: 2 });
    this.documentContent.content.push({
      image: this.chartImage,
      width: 500,
      height: 250,
      style: "center",
      lineHeight: 2,
    });
    this.documentContent.content.push({ text: " ", style: "subheader", lineHeight: 1 });
  }

  /**
   * Add accesses table to the PDF.
   */
  addAccessesTable() {
    const tableData = this.accesses.map((row) => {
      const result = {
        timestamp: moment(row.timestamp).format("L LTS"),
        tool: row.tool,
        access_kind: row.access_kind,
        justification: row.justification,
        data_types: row.data_types.join(", "),
      };
      return result;
    });

    this.documentContent.content.push({ text: "Alle Datenzugriffe", style: "subheader", lineHeight: 1.5 });
    let tableContent = [];
    // Add headers in the same order as they appear in the object
    const header = Object.keys(tableData[0]).map((element) => ({
      text: tableHeaderContent[element],
      style: "boldContent",
    }));
    tableContent.push(header);
    tableData.forEach((row) => {
      tableContent.push(Object.values(row).map((value) => ({ text: value })));
    });

    this.documentContent.content.push({
      layout: "lightHorizontalLines",
      table: {
        headerRows: 1,
        widths: [90, 70, 70, 110, 110],
        body: tableContent,
      },
    });
  }
}

export default PdfGenerator;
