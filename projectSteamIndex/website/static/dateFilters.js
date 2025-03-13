function pastWeek(){
    const today = new Date();
    const startDate = new Date(today);
    startDate.setDate(today.getDate() - 7);
    const startDateString = startDate.toLocaleDateString('en-CA')
    const endDateString = today.toLocaleDateString('en-CA')
    return {
        startDate: startDateString,
        endDate: endDateString
    };
}

function pastMonth() {
    const today = new Date();
    const startDate = new Date(today);

    // Adjust month and handle potential month boundary issues
    startDate.setMonth(today.getMonth() - 1);

    // Format dates to YYYY-MM-DD
    const startDateString = startDate.toLocaleDateString('en-CA');
    const endDateString = today.toLocaleDateString('en-CA');
    // Return the dates as an object
    return {
        startDate: startDateString,
        endDate: endDateString
    };
}

const weekDateMapping = {
    "Pre Week 1": { startDate: "2024-08-01", endDate: "2024-08-11" },
    "Pre Week 2": { startDate: "2024-08-11", endDate: "2024-08-18" },
    "Pre Week 3": { startDate: "2024-08-18", endDate: "2024-08-25" },
    "Week 1": { startDate: "2024-08-25", endDate: "2024-09-08" },
    "Week 2": { startDate: "2024-09-08", endDate: "2024-09-15" },
    "Week 3": { startDate: "2024-09-15", endDate: "2024-09-22" },
    "Week 4": { startDate: "2024-09-22", endDate: "2024-09-29" },
    "Week 5": { startDate: "2024-09-29", endDate: "2024-10-06" },
    "Week 6": { startDate: "2024-10-06", endDate: "2024-10-13" },
    "Week 7": { startDate: "2024-10-13", endDate: "2024-10-20" },
    "Week 8": { startDate: "2024-10-20", endDate: "2024-10-27" },
    "Week 9": { startDate: "2024-10-27", endDate: "2024-11-03" },
    "Week 10": { startDate: "2024-11-03", endDate: "2024-11-10" },
    "Week 11": { startDate: "2024-11-10", endDate: "2024-11-17" },
    "Week 12": { startDate: "2024-11-17", endDate: "2024-11-24" },
    "Week 13": { startDate: "2024-11-24", endDate: "2024-12-01" },
    "Week 14": { startDate: "2024-12-01", endDate: "2024-12-08" },
    "Week 15": { startDate: "2024-12-08", endDate: "2024-12-15" },
    "Week 16": { startDate: "2024-12-15", endDate: "2024-12-22" },
    "Week 17": { startDate: "2024-12-22", endDate: "2024-12-29" },
    "Week 18": { startDate: "2024-12-29", endDate: "2025-01-05" }
};

function getWeek(week) {
    return weekDateMapping[week];
}