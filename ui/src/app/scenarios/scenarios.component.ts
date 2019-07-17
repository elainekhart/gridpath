import { Component, OnInit } from '@angular/core';
import { Scenario } from './scenario';
import { ScenariosService} from "./scenarios.service";
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-scenarios',
  templateUrl: './scenarios.component.html',
  styleUrls: ['./scenarios.component.css']
})

export class ScenariosComponent implements OnInit {

  scenarios: Scenario[];
  selectedScenario: Scenario;
  selectedId: number;

  constructor(private scenariosService: ScenariosService,
              private route: ActivatedRoute) {
    console.log("Constructing scenarios...");
  }

  ngOnInit() {
    console.log("Initializing scenarios...");
    this.getScenarios();
  }

  // onSelect(scenario: Scenario): void {
  //   this.selectedScenario = scenario;
  // }

  getScenarios(): void {
    console.log("Getting scenarios...");
    this.scenariosService.getScenarios()
      .subscribe(scenarios => this.scenarios = scenarios);
  }

  updateScenarios(event): void{
    console.log('Updating scenarios...');
    this.getScenarios()
  }

}

