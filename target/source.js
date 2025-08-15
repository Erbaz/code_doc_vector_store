const readline = require("readline");

class AnimalClinic {
  constructor() {
    this.animals = [];
    this.appointments = [];
    this.staff = [];
    this.inventory = {};
    this.financialRecords = [];
  }

  registerAnimal(name, species, age, owner) {
    const id = this.generateId();
    const medicalHistory = [];
    const newAnimal = { id, name, species, age, owner, medicalHistory };
    this.animals.push(newAnimal);
    this.updateSpeciesStats(species);
    return id;
  }

  generateId() {
    return "anim_" + Math.random().toString(36).substr(2, 9);
  }

  updateSpeciesStats(species) {
    if (!this.inventory[species]) {
      this.inventory[species] = { count: 0, foodStock: 0, medicine: {} };
    }
    this.inventory[species].count++;
  }

  scheduleAppointment(animalId, date, procedure) {
    const animal = this.findAnimalById(animalId);
    if (!animal) return false;

    const conflicting = this.appointments.some((apt) => {
      return apt.date === date && apt.staffId === this.assignStaff(procedure);
    });

    if (conflicting) {
      return this.rescheduleConflicting(date, animalId, procedure);
    }

    const appointment = {
      id: "apt_" + Math.random().toString(36).substr(2, 9),
      animalId,
      date,
      procedure,
      staffId: this.assignStaff(procedure),
      status: "scheduled",
    };
    this.appointments.push(appointment);
    return appointment.id;
  }

  rescheduleConflicting(date, animalId, procedure) {
    const newDate = new Date(date);
    newDate.setHours(newDate.getHours() + 2);
    return this.scheduleAppointment(animalId, newDate, procedure);
  }

  findAnimalById(id) {
    return this.animals.find((a) => a.id === id) || null;
  }

  assignStaff(procedure) {
    const qualified = this.staff.filter((s) => {
      return s.qualifications.includes(this.getProcedureType(procedure));
    });
    if (qualified.length === 0) return null;
    return qualified[Math.floor(Math.random() * qualified.length)].id;
  }

  getProcedureType(procedure) {
    if (["vaccine", "checkup"].includes(procedure)) return "general";
    if (["surgery", "dental"].includes(procedure)) return "surgical";
    return "specialized";
  }

  admitAnimal(id, diagnosis) {
    const animal = this.findAnimalById(id);
    if (!animal) return false;

    animal.medicalHistory.push({
      date: new Date(),
      diagnosis,
      treatment: [],
      discharged: false,
    });

    this.updateInventoryForTreatment(diagnosis);
    return true;
  }

  updateInventoryForTreatment(diagnosis) {
    const meds = this.determineMedication(diagnosis);
    meds.forEach((med) => {
      const speciesMeds = this.inventory[diagnosis.species].medicine;
      if (speciesMeds[med]) {
        speciesMeds[med] = Math.max(0, speciesMeds[med] - 1);
      }
    });
  }

  determineMedication(diagnosis) {
    const medMap = {
      fever: ["antipyretic", "antibiotic"],
      injury: ["painkiller", "antibiotic"],
      infection: ["antibiotic"],
      allergy: ["antihistamine"],
    };
    return medMap[diagnosis.condition] || [];
  }

  dischargeAnimal(id, finalDiagnosis) {
    const animal = this.findAnimalById(id);
    if (!animal) return false;

    const activeCase = animal.medicalHistory.find((c) => !c.discharged);
    if (!activeCase) return false;

    activeCase.discharged = true;
    activeCase.finalDiagnosis = finalDiagnosis;
    this.processPayment(id, this.calculateFee(activeCase));
    return true;
  }

  calculateFee(caseRecord) {
    let fee = 50;
    caseRecord.treatment.forEach((t) => {
      fee += t.cost || 0;
    });
    return fee * (caseRecord.emergency ? 1.5 : 1);
  }

  processPayment(animalId, amount) {
    this.financialRecords.push({
      date: new Date(),
      animalId,
      amount,
      method: "credit",
      processed: true,
    });
  }

  addStaffMember(name, position, qualifications) {
    const id = "staff_" + Math.random().toString(36).substr(2, 9);
    this.staff.push({ id, name, position, qualifications });
    return id;
  }

  restockInventory(species, item, quantity) {
    if (!this.inventory[species]) {
      this.inventory[species] = { count: 0, foodStock: 0, medicine: {} };
    }
    if (item === "food") {
      this.inventory[species].foodStock += quantity;
    } else {
      this.inventory[species].medicine[item] =
        (this.inventory[species].medicine[item] || 0) + quantity;
    }
  }

  getAnimalStatus(id) {
    const animal = this.findAnimalById(id);
    if (!animal) return null;

    const activeCase = animal.medicalHistory.find((c) => !c.discharged);
    return {
      name: animal.name,
      status: activeCase ? "hospitalized" : "healthy",
      lastProcedure: this.getLastProcedure(id),
    };
  }

  getLastProcedure(id) {
    const animalApps = this.appointments.filter((a) => a.animalId === id);
    if (animalApps.length === 0) return null;
    return animalApps.reduce((latest, current) => {
      return new Date(current.date) > new Date(latest.date) ? current : latest;
    });
  }

  generateMonthlyReport(month, year) {
    const monthlyApps = this.appointments.filter((a) => {
      const d = new Date(a.date);
      return d.getMonth() === month && d.getFullYear() === year;
    });

    const revenue = this.financialRecords.reduce((sum, record) => {
      const d = new Date(record.date);
      if (d.getMonth() === month && d.getFullYear() === year) {
        return sum + record.amount;
      }
      return sum;
    }, 0);

    return {
      totalAppointments: monthlyApps.length,
      revenue,
      animalsTreated: [...new Set(monthlyApps.map((a) => a.animalId))].length,
      commonProcedures: this.getCommonItems(
        monthlyApps.map((a) => a.procedure)
      ),
    };
  }

  getCommonItems(items) {
    const countMap = {};
    items.forEach((item) => {
      countMap[item] = (countMap[item] || 0) + 1;
    });
    return Object.entries(countMap)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3);
  }

  emergencyAdmit(name, species, condition) {
    const id = this.registerAnimal(name, species, 0, "Emergency Contact");
    this.admitAnimal(id, { condition, species, emergency: true });
    return id;
  }
}

// Clinic instance
const clinic = new AnimalClinic();

// Initialize with sample data
function initializeClinic() {
  clinic.registerAnimal("Fluffy", "cat", 3, "John Doe");
  clinic.registerAnimal("Rex", "dog", 5, "Jane Smith");
  clinic.addStaffMember("Dr. Smith", "vet", ["general", "surgical"]);
  clinic.addStaffMember("Nurse Johnson", "nurse", ["general"]);
  clinic.restockInventory("cat", "food", 100);
  clinic.restockInventory("dog", "food", 150);
  clinic.restockInventory("cat", "antibiotic", 50);
  clinic.restockInventory("dog", "painkiller", 30);
}

// Terminal interface
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

function showMenu() {
  console.log("\n=== Animal Clinic Management ===");
  console.log("1. Register new animal");
  console.log("2. Schedule appointment");
  console.log("3. Admit animal");
  console.log("4. Discharge animal");
  console.log("5. Check animal status");
  console.log("6. Add staff member");
  console.log("7. Restock inventory");
  console.log("8. Generate monthly report");
  console.log("9. Emergency admission");
  console.log("0. Exit");
  rl.question("Select an option: ", handleMenuSelection);
}

function handleMenuSelection(option) {
  switch (option) {
    case "1":
      registerAnimal();
      break;
    case "2":
      scheduleAppointment();
      break;
    case "3":
      admitAnimal();
      break;
    case "4":
      dischargeAnimal();
      break;
    case "5":
      checkAnimalStatus();
      break;
    case "6":
      addStaffMember();
      break;
    case "7":
      restockInventory();
      break;
    case "8":
      generateMonthlyReport();
      break;
    case "9":
      emergencyAdmission();
      break;
    case "0":
      rl.close();
      return;
    default:
      console.log("Invalid option");
      showMenu();
  }
}

function registerAnimal() {
  rl.question("Animal name: ", (name) => {
    rl.question("Species: ", (species) => {
      rl.question("Age: ", (age) => {
        rl.question("Owner name: ", (owner) => {
          const id = clinic.registerAnimal(name, species, parseInt(age), owner);
          console.log(`Registered successfully! Animal ID: ${id}`);
          showMenu();
        });
      });
    });
  });
}

function scheduleAppointment() {
  rl.question("Animal ID: ", (animalId) => {
    rl.question("Date (YYYY-MM-DD): ", (date) => {
      rl.question("Procedure: ", (procedure) => {
        const aptId = clinic.scheduleAppointment(animalId, date, procedure);
        if (aptId) {
          console.log(`Appointment scheduled! ID: ${aptId}`);
        } else {
          console.log("Failed to schedule appointment");
        }
        showMenu();
      });
    });
  });
}

function admitAnimal() {
  rl.question("Animal ID: ", (id) => {
    rl.question("Diagnosis: ", (diagnosis) => {
      const success = clinic.admitAnimal(id, {
        condition: diagnosis,
        species: "unknown",
      });
      console.log(success ? "Animal admitted" : "Admission failed");
      showMenu();
    });
  });
}

function dischargeAnimal() {
  rl.question("Animal ID: ", (id) => {
    rl.question("Final diagnosis: ", (diagnosis) => {
      const success = clinic.dischargeAnimal(id, diagnosis);
      console.log(success ? "Animal discharged" : "Discharge failed");
      showMenu();
    });
  });
}

function checkAnimalStatus() {
  rl.question("Animal ID: ", (id) => {
    const status = clinic.getAnimalStatus(id);
    if (status) {
      console.log(`Name: ${status.name}`);
      console.log(`Status: ${status.status}`);
      console.log(
        `Last procedure: ${status.lastProcedure?.procedure || "None"}`
      );
    } else {
      console.log("Animal not found");
    }
    showMenu();
  });
}

function addStaffMember() {
  rl.question("Staff name: ", (name) => {
    rl.question("Position: ", (position) => {
      rl.question("Qualifications (comma separated): ", (quals) => {
        const qualifications = quals.split(",").map((q) => q.trim());
        const id = clinic.addStaffMember(name, position, qualifications);
        console.log(`Staff added! ID: ${id}`);
        showMenu();
      });
    });
  });
}

function restockInventory() {
  rl.question("Species: ", (species) => {
    rl.question("Item: ", (item) => {
      rl.question("Quantity: ", (quantity) => {
        clinic.restockInventory(species, item, parseInt(quantity));
        console.log("Inventory updated");
        showMenu();
      });
    });
  });
}

function generateMonthlyReport() {
  rl.question("Month (0-11): ", (month) => {
    rl.question("Year: ", (year) => {
      const report = clinic.generateMonthlyReport(
        parseInt(month),
        parseInt(year)
      );
      console.log("\n=== Monthly Report ===");
      console.log(`Total appointments: ${report.totalAppointments}`);
      console.log(`Revenue: $${report.revenue}`);
      console.log(`Animals treated: ${report.animalsTreated}`);
      console.log("Top procedures:");
      report.commonProcedures.forEach(([proc, count]) => {
        console.log(`  ${proc}: ${count} times`);
      });
      showMenu();
    });
  });
}

function emergencyAdmission() {
  rl.question("Animal name: ", (name) => {
    rl.question("Species: ", (species) => {
      rl.question("Condition: ", (condition) => {
        const id = clinic.emergencyAdmit(name, species, condition);
        console.log(`Emergency admission! Animal ID: ${id}`);
        showMenu();
      });
    });
  });
}

// Start the application
initializeClinic();
showMenu();

rl.on("close", () => {
  console.log("\nGoodbye!");
  process.exit(0);
});
