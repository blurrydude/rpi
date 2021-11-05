import { OnInit, Component, ElementRef, Input, Output, ViewChild } from '@angular/core';
import { StatusService } from "../../services/status.service";
import { GoogleChartComponent } from 'angular-google-charts';  

@Component({
  selector: 'home',
  templateUrl: './home.component.html'
})
export class HomeComponent implements OnInit {
    @Output() status: SystemState = new SystemState({});
    @Output() minerStatus: any = {};
    @Output() ltcPrice: any = {};
    @Output() tezosPrice: any = {};
    @Output() algoPrice: any = {};
    @Output() tezosExchange: any = {};
    @Output() ltcExchange: any = {};
    @Output() poolStatus: any = {};
    @Output() fast: boolean = true;
    @Output() live: boolean = true;
    @Output() local: boolean = true;
    @Output() loghours: number = 2;
    firstLoad: boolean = true;
    logtick: number = 0;
    canvasX: number = 0;
    canvasY: number = 0;
    scale: number = 1.6;
    roll: number = 0;

    @ViewChild('myCanvas', { static: true })
    myCanvas!: ElementRef;
    public context!: CanvasRenderingContext2D;

    @Output() @Input() chartData: any = {
      title: 'Temperatures',
      //type: 'ComboChart',
      type: 'LineChart',
      data: [
      ],
      columnNames: ['',
        'Game Room Temperature',
        //'GR Hum',
        //'GR Cool',
        //'GR Heat',
        //'GR Fan',
        //'WHF',
        'Main Temperature',
        //'HW Hum',
        //'HW Cool',
        //'HW Heat',
        //'HW Fan',
        //'WHF',
        'Day Room Temperature',
        //'DR Hum',
        'Deck Temperature',
        //'Deck Hum'
        'Game Room Cooling',
        'Game Room Heating',
        'Game Room Fan',
        'Main Cooling',
        'Main Heating',
        'Main Fan',
        'Whole House Fan'
      ],
      options: {
        backgroundColor: "#212529",
        titleTextStyle: {
          color: "#fff"
        },
        legend: {
          textStyle: {
            color: "#fff"
          },
          titleTextStyle: {
            color: "#fff"
          }
        },
        hAxis: {
           title: '',
           textStyle: {
             color: "#fff"
           },
           titleTextStyle: {
             color: "#fff"
           }
        },
        vAxis:{
           title: 'Temperature',
          textStyle: {
            color: "#fff"
          },
          titleTextStyle: {
            color: "#fff"
          },
           gridlines: {
             color: "#777"
           }
        },
       series: {
        0: {lineWidth: 1},
        1: {lineWidth: 3},
        2: {lineWidth: 1},
        3: {lineWidth: 2},
        4: {lineWidth: 1},
        5: {lineWidth: 1},
        6: {lineWidth: 1},
        7: {lineWidth: 1},
        8: {lineWidth: 1},
        9: {lineWidth: 1},
        10: {lineWidth: 1}
      },
        colors: [
          '#ff9999',

          '#ff0000',
          
          '#ffaaaa',
          '#ffcccc',

          '#ff99ff',
          '#99ffff',
          '#99ff99',
          '#ff00ff',
          '#00ffff',
          '#00ff00',
          '#007700',
        ],
      lineWidth: 3
      },
      width: 1295,
      height: 800
    }

    @Output() @Input() chartData2: any = {
      title: 'Power',
      //type: 'ComboChart',
      type: 'LineChart',
      data: [
      ],
      columnNames: [''],
      options: {
        backgroundColor: "#212529",
        titleTextStyle: {
          color: "#fff"
        },
        legend: {
          textStyle: {
            color: "#fff"
          },
          titleTextStyle: {
            color: "#fff"
          }
        },
        hAxis: {
           title: '',
           textStyle: {
             color: "#fff"
           },
           titleTextStyle: {
             color: "#fff"
           }
        },
        vAxis:{
           title: 'Power (W)',
           textStyle: {
             color: "#fff"
           },
           titleTextStyle: {
             color: "#fff"
           },
            gridlines: {
              color: "#777"
            }
          //  viewWindow: {
          //   max:85,
          //   min:55
          // }
        },
        lineWidth: 2
      },
      width: 1295,
      height: 800
    }

    @Output() @Input() chartData3: any = {
      title: 'Power',
      //type: 'ComboChart',
      type: 'Gauge',
      data: [
        ["Power (kW)",0]
      ],
      options: {
        backgroundColor: "#212529",
        width: 200,
        height: 200,
        greenFrom: 0,
        greenTo: 25,
        redFrom: 60,
        redTo: 100,
        yellowFrom: 25,
        yellowTo: 60,
        minorTicks: 5,
        majorTicks: ['0W','250W','500W','750W','1kW']  // <-- add major ticks
      }
      // width: 1295,
      // height: 800
    }

    @Output() @Input() chartData4: any = {
      title: 'Humidities',
      //type: 'ComboChart',
      type: 'LineChart',
      data: [
      ],
      columnNames: ['',
        //'GR Temp',
        'Game Room Humidity',
        //'GR Cool',
        //'GR Heat',
        //'GR Fan',
        //'WHF',
        //'HW Temp',
        'Main Humidity',
        //'HW Cool',
        //'HW Heat',
        //'HW Fan',
        //'WHF',
        //'DR Temp',
        'Day Room Humidity',
        //'Deck Temp',
        'Deck Humidity',
        //'Game Room Cooling',
        //'Game Room Heating',
        //'Game Room Fan',
        //'Main Cooling',
        //'Main Heating',
        //'Main Fan',
        //'Whole House Fan'
      ],
      options: {
        backgroundColor: "#212529",
        titleTextStyle: {
          color: "#fff"
        },
        legend: {
          textStyle: {
            color: "#fff"
          },
          titleTextStyle: {
            color: "#fff"
          }
        },
        hAxis: {
           title: '',
           textStyle: {
             color: "#fff"
           },
           titleTextStyle: {
             color: "#fff"
           }
        },
        vAxis:{
           title: 'Power (W)',
           textStyle: {
             color: "#fff"
           },
           titleTextStyle: {
             color: "#fff"
           },
            gridlines: {
              color: "#777"
            }
          //  viewWindow: {
          //   max:85,
          //   min:55
          // }
        },
        series: {
         0: {lineWidth: 1},
         1: {lineWidth: 3},
         2: {lineWidth: 1},
         3: {lineWidth: 2},
         4: {lineWidth: 1},
         5: {lineWidth: 1},
         6: {lineWidth: 1},
         7: {lineWidth: 1},
         8: {lineWidth: 1},
         9: {lineWidth: 1},
         10: {lineWidth: 1}
       },
        colors: [
          //'#ff9999',
          '#9999ff',
          //'#ff99ff',
          //'#99ffff',
          //'#99ff99',
          //'#337733',
  
          //'#ff0000',
          '#0000ff',
          //'#ff00ff',
          //'#00ffff',
          //'#00ff00',
          //'#007700',
          
          //'#ffaaaa',
          '#aaaaff',
          //'#ffcccc',
          '#ccccff',
          '#ff99ff',
          '#99ffff',
          '#99ff99',
          '#ff00ff',
          '#00ffff',
          '#00ff00',
          '#007700',
        ],
        lineWidth: 2
      },
      width: 1295,
      height: 800
    }

    housepoints = [
      [482,54],
      [551,54],
      [724,54],
      [76,105],
      [185,105],
      [412,105],
      [443,105],
      [482,105],
      [76,132],
      [185,132],
      [412,138],
      [443,138],
      [586,142],
      [653,142],
      [724,142],
      [412,175],
      [421,175],
      [429,175],
      [437,175],
      [443,175],
      [445,175],
      [453,175],
      [462,175],
      [482,175],
      [551,175],
      [586,175],
      [653,175],
      [724,175],
      [185,206],
      [316,206],
      [370,206],
      [412,206],
      [421,206],
      [429,206],
      [437,206],
      [445,206],
      [453,206],
      [462,206],
      [484,206],
      [504,206],
      [533,206],
      [551,206],
      [586,206],
      [337,230],
      [370,230],
      [533,233],
      [551,233],
      [566,233],
      [411,238],
      [484,238],
      [504,238],
      [76,245],
      [185,245],
      [484,262],
      [504,262],
      [49,271],
      [58,271],
      [67,271],
      [76,271],
      [316,281],
      [337,281],
      [538,284],
      [551,284],
      [566,284],
      [49,299],
      [58,299],
      [67,299],
      [76,299],
      [484,304],
      [505,304],
      [551,304],
      [587,304],
      [724,304],
      [310,336],
      [341,336],
      [185,360],
      [310,360],
      [341,360],
      [411,360],
      [484,360],
      [475,422],
      [504,422],
      [725,422],
      [475,510],
      [504,510],
      [475,548],
      [535,548],
      [185,550],
      [475,585],
      [535,585],
      [596,585],
      [725,585],
      [185,592],
      [194,592],
      [203,592],
      [212,592],
      [596,618],
      [642,618],
      [185,620],
      [194,620],
      [203,620],
      [212,620],
      [76,628],
      [185,628],
      [475,668],
      [596,668],
      [642,668],
      [725,668],
      [411,550],
      [587,233],

      [374,105],
      [402,105],
      [412,113],
      [482,123],
      [412,134],
      [667,142],
      [715,142],
      [482,169],
      [528,175],
      [545,175],
      [560,175],
      [580,175],
      [601,175],
      [646,175],
      [586,186],
      [586,201],
      [382,206],
      [405,206],
      [512,206],
      [530,206],
      [185,217],
      [411,218],
      [411,232],
      [571,233],
      [584,233],
      [185,241],
      [411,242],
      [587,242],
      [104,245],
      [160,245],
      [587,258],
      [316,284],
      [316,336],
      [342,336],
      [204,360],
      [294,360],
      [516,422],
      [588,422],
      [612,422],
      [690,422],
      [185,434],
      [185,497],
      [562,585],
      [581,585],
      [633,585],
      [654,585],
      [204,206],
      [294,206],

      [388,30],
      [545,65],
      [561,65],
      [387,94],
      [351,113],
      [177,144],
      [195,165],
      [525,183],
      [525,193],
      [569,193],
      [133,194],
      [367,202],
      [571,222],
      [597,223],
      [355,266],
      [524,266],
      [577,269],
      [253,283],
      [82,306],
      [432,311],
      [472,312],
      [386,349],
      [288,371],
      [182,410],
      [600,416],
      [319,459],
      [652,497],
      [182,506],
      [670,518],
      [307,544],
      [507,570],
      [684,635],
      [547,639],
      // [228,548],
      // [298,548],
      // [371,548],
    ];
    houselines = [
      [0,2],
      [0,23],
      [3,7],
      [3,102],
      [8,9],
      [4,103],
      [102,103],
      [92,95],
      [95,101],
      [98,101],
      [93,99],
      [94,100],
      [55,58],
      [55,64],
      [64,67],
      [56,65],
      [57,66],
      [51,52],
      [28,42],
      [5,48],
      [6,19],
      [15,27],
      [10,11],
      [1,24],
      [12,71],
      [12,14],
      [13,26],
      [2,72],
      [16,32],
      [17,33],
      [18,34],
      [20,35],
      [21,36],
      [22,37],
      [29,59],
      [59,60],
      [43,60],
      [43,44],
      [30,44],
      [48,50],
      [38,79],
      [75,79],
      [73,76],
      [73,74],
      [74,77],
      [78,108],
      [87,108],
      [68,72],
      [39,69],
      [53,54],
      [41,70],
      [40,45],
      [45,109],
      [45,61],
      [61,63],
      [47,63],

      [80,82],
      [80,104],
      [82,107],
      [104,107],
      [81,84],
      [83,84],
      [85,86],
      [86,89],
      [88,91],
      [90,105],
      [96,97],
      [97,106]
    ];
    housedoors = [
      [110,111],
      [112,114],
      [130,135],
      [138,139],
      [144,145],
      [131,132],
      [150,151],
      [126,127],
      [113,117],
      [128,129],
      [118,119],
      [120,121],
      [115,116],
      [124,125],
      [122,123],
      [133,134],
      [137,140],
      [152,153],
      [154,155],
      [146,147],
      [148,149],
      [156,157]
    ];
    housecircuits = [
      "Lamp post",
      "Gym Lamp",
      "Library Lamp",
      "Porch",
      "Livingroom TV",
      "Day Room Lamp",
      "Fireplace",
      "Floor Fan",
      "Hallway",
      "Whole House Fan",
      "Day Room Fan",
      "Livingroom Lamp",
      "Shower Fan",
      "Bedroom Lamp",
      "Bar",
      "Guest Bath",
      "Master Bath",
      "Dining Room",
      "Deck Rail",
      "Kitchen",
      "Under Cabinet",
      "Coffee Station",
      "Circulating Fan",
      "Deck Fountain",
      "Lamp post",
      "Game Room",
      "Shop Light",
      "Deck Light",
      "Bench Fan",
      "Game Tables",
      "Stairway",
      "Storage Room",
      "Laundry Room"
    ];
    houselabelpoints = [
      [280,160],
      [235,300],
      [350,280],
      [420,325],
      [115,210],
      [480,192],
      [510,90],
      [630,90],
      [512,295],
      [552,295],
      [554,214],
      [640,225],
      [280,450],
      [125,450],
      [492,557],
      [535,625],
      [672,620],
      [645,480]
    ];
    houselabels = [
      "Livingroom",
      "Dining Room",
      "Bar",
      "Kitchen",
      "Day Room",
      "Hallway",
      "Gym",
      "Library",
      "Guest Bath",
      "Master Bath",
      "Shower",
      "Bedroom",
      "Game Room",
      "Deck",
      "Stairway",
      "Laundry",
      "Storage",
      "Shop"
    ];

    constructor(public httpMessageService: StatusService) { 
      this.load(httpMessageService, true);
    }

    public canvasClick(event: any) {
      let clickX = event.clientX-this.canvasX;
      let clickY = event.clientY-this.canvasY+window.pageYOffset;
      console.log("clicked "+clickX+" "+clickY);
      for(let i = 158; i < this.housepoints.length; i++) {
        let p = this.housepoints[i];
        let c = this.housecircuits[i - 158];
        let l = p[0]*this.scale - 8;
        let r = p[0]*this.scale + 8;
        let t = p[1]*this.scale - 8;
        let b = p[1]*this.scale + 8;
        if(clickX >= l && clickX <= r && clickY >= t && clickY <= b) {
          console.log(c+" clicked!");
          this.status.circuits?.forEach(circuit => {
            if(circuit.name == c) {
              let state = circuit.status.relay.on ? "off" : "on";
              this.command("turn "+circuit.name.toLowerCase()+" "+state);
            }
          });
        }
      }
    }

    ngOnInit(): void {
      console.log("I inited.");
      let rect = this.myCanvas.nativeElement.getBoundingClientRect();
      this.canvasX = rect.x;
      this.canvasY = rect.y;
      this.context = this.myCanvas.nativeElement.getContext('2d');
      
      this.drawFloors();
      this.drawDoors();
      this.drawLabels();
    }

    public redraw() {
      this.context.clearRect(0,0,2000,2000);
      this.drawFloors();
      this.drawDoors();
      this.drawLabels();
      this.drawCircuits();
    }

    public drawLabels() {
      this.context.fillStyle = '#ffcc77';
      let i = 0;
      this.houselabelpoints.forEach(lp => {
        let text = this.houselabels[i];
        this.context.fillText(text,lp[0]*this.scale,lp[1]*this.scale);
        i++;
      });
    }

    public drawFloors() {
      this.context.strokeStyle = '#009900';
      this.context.lineWidth = 3;
      this.context.beginPath();
      this.houselines.forEach(line => {
        let p1 = this.housepoints[line[0]];
        let p2 = this.housepoints[line[1]];
        this.context.moveTo(p1[0]*this.scale,p1[1]*this.scale);
        this.context.lineTo(p2[0]*this.scale,p2[1]*this.scale);
      });
      this.context.stroke();
    }

    public drawDoors() {
      this.context.strokeStyle = '#004400';
      this.context.lineWidth = 3;
      this.context.beginPath();
      this.housedoors.forEach(door => {
        let p1 = this.housepoints[door[0]];
        let p2 = this.housepoints[door[1]];
        this.context.moveTo(p1[0]*this.scale,p1[1]*this.scale);
        this.context.lineTo(p2[0]*this.scale,p2[1]*this.scale);
      });
      this.context.stroke();
    }

    public drawCircuits() {
      let i = 0;
      this.context.lineWidth = 1;
      this.housepoints.forEach(point => {
        let x = point[0];
        let y = point[1];
        //this.context.fillRect(x*this.scale,y*this.scale,2,2);
        if (i > 157) {
          let cindex = i - 158;
          let state = "off";
          let power = "0 W";
          let circuitname = this.housecircuits[cindex];
          this.status.circuits?.forEach(circuit => {
            if(circuit.name == circuitname) {
              state = circuit.status.relay.on ? "on" : "off";
              power = circuit.status.relay.power + " W";
            }
          });
          //this.context.fillText(cindex+'',x+3,y+3);
          let shape = [[0,0]];
          if(circuitname.indexOf("Fan")> -1) {
            shape = this.fanshape(x*this.scale,y*this.scale);
            this.context.strokeStyle = '#7777ff';
          } else if(circuitname.indexOf("TV")> -1) {
            shape = this.tvshape(x*this.scale,y*this.scale);
            this.context.strokeStyle = '#ff7777';
          } else {
            shape = this.bulbshape(x*this.scale,y*this.scale);
            this.context.strokeStyle = '#ffff00';
          }
          if(state=="off"){
            this.context.strokeStyle = '#999999';
          }
          
          this.context.beginPath();
          this.context.moveTo(shape[0][0],shape[0][1]);
          shape.forEach(bp => {
            this.context.lineTo(bp[0],bp[1]);
          });
          this.context.stroke();
          this.context.fillStyle = '#cccccc';
          this.context.fillText(power,x*this.scale+8,y*this.scale-6);
        }
        i++;
      });
    }

    public tvshape(x:number, y:number) {
      return [
        [x-20,y-2],
        [x+20,y-2],
        [x+22,y+2],
        [x+22,y+3],
        [x-22,y+3],
        [x-22,y+2],
        [x-20,y-2]
      ];
    }

    public bulbshape(x:number, y:number) {
      return [
        [x-5,y],
        [x-3,y-3],
        [x,y-5],
        [x+3,y-3],
        [x+5,y],
        [x+3,y+2],
        [x+2,y+7],
        [x-2,y+7],
        [x-3,y+2],
        [x-5,y]
      ];
    }

    public fanshape(x:number, y:number) {
      return [
        [x-3,y-1],
        [x-1,y-3],
        [x-2,y-6],
        [x-4,y-6],
        [x-6,y-4],
        [x-6,y-2],
        [x-3,y-1],
        [x-1,y-3],

        [x+1,y-3],
        [x+3,y-1],
        [x+6,y-2],
        [x+6,y-4],
        [x+4,y-6],
        [x+2,y-6],
        [x+1,y-3],
        [x+3,y-1],

        [x+3,y+1],
        [x+1,y+3],
        [x+2,y+6],
        [x+4,y+6],
        [x+6,y+4],
        [x+6,y+2],
        [x+3,y+1],
        [x+1,y+3],

        [x-1,y+3],
        [x-3,y+1],
        [x-6,y+2],
        [x-6,y+4],
        [x-4,y+6],
        [x-2,y+6],
        [x-1,y+3],
        [x-3,y+1],

        [x-3,y-1]
      ];
    }

    public command(com: string) {
      this.httpMessageService.sendCommand(com).toPromise().then(smsg => {
        console.log("sent: "+com);
        setTimeout(()=>{this.load(this.httpMessageService,false)},1000);
      });
    }

    public set_command(room: string, setting: string, value: any) {
      this.command("set "+room+" "+setting+":"+value);
    }

    public load(httpMessageService: StatusService, main_loop: boolean) {
      if(main_loop == true) setTimeout(()=>{this.load(httpMessageService, true)},this.fast?5000:15000);
      if(this.live == false && this.firstLoad == false) return;
      if(this.firstLoad == true) this.firstLoad = false;
      this.httpMessageService.getStatus().toPromise().then(msg => {
        this.status = new SystemState(msg);
        this.redraw();
        // this.totalPower = 0.0;
        // for (const [k, v] of Object.entries(this.status)) {
        //   if(this.chartData2.columnNames.indexOf(k)===-1) {
        //     this.chartData2.columnNames.push(k);
        //   }
        //   this.totalPower += parseFloat(v["power"])
        // }
        // if(this.chartData2.columnNames.indexOf("Total")===-1) {
        //   this.chartData2.columnNames.push("Total");
        // }
      });
      if(this.roll == 0) {
        this.httpMessageService.getMinerStatus().toPromise().then(msg => {
          this.minerStatus = msg;
        });
        this.httpMessageService.getCoinPrice("LTC-USD").toPromise().then(msg => {
          this.ltcPrice = msg;
        });
        this.httpMessageService.getCoinPrice("ALGO-USD").toPromise().then(msg => {
          this.algoPrice = msg;
        });
        this.httpMessageService.getCoinPrice("XTZ-USD").toPromise().then(msg => {
          this.tezosPrice = msg;
        });
        this.httpMessageService.getExchangeRates("XTZ").toPromise().then(msg => {
          this.tezosExchange = msg;
        });
        this.httpMessageService.getExchangeRates("LTC").toPromise().then(msg => {
          this.ltcExchange = msg;
        });
        this.httpMessageService.getPoolStatus().toPromise().then(msg => {
          this.poolStatus = msg;
        });
      } 
      if(this.roll < 5) {
        this.roll++;
      } else {
        this.roll = 0;
      }
    }
}
export class SystemState {
  peers?: (PeersEntity)[] | null;
  thermostats?: (ThermostatsEntity)[] | null;
  rollershades?: (RollershadesEntity)[] | null;
  circuits?: (CircuitsEntity)[] | null;
  public constructor(d: any) {
    this.peers = d.peers;
    this.thermostats = d.thermostats;
    this.rollershades = d.rollershades;
    this.circuits = d.circuits;
  }
}
export class PeersEntity {
  id: number;
  name: string;
  ip_address: string;
  model: string;
  circuit_authority: boolean;
  timestamp: string;
  thermostat: boolean;
  rollershade: boolean;
  rollerdoor: boolean;
  public constructor(d: any) {
    this.id = d.id;
    this.name = d.name;
    this.ip_address = d.ip_address;
    this.model = d.model;
    this.circuit_authority = d.circuit_authority;
    this.timestamp = d.timestamp;
    this.thermostat = d.thermostat;
    this.rollershade = d.rollershade;
    this.rollerdoor = d.rollerdoor;
  }
}
export class ThermostatsEntity {
  room: string;
  settings: Settings;
  state: State;
  public constructor(d: any) {
    this.room = d.room;
    this.settings = d.settings;
    this.state = d.state;
  }
}
export class Settings {
  failed_read_halt_limit: number;
  temperature_high_setting: number;
  temperature_low_setting: number;
  humidity_setting: number;
  air_circulation_minutes: number;
  circulation_cycle_minutes: number;
  ventilation_cycle_minutes: number;
  stage_limit_minutes: number;
  stage_cooldown_minutes: number;
  use_whole_house_fan: boolean;
  system_disabled: boolean;
  swing_temp_offset: number;
  public constructor(d: any) {
    this.failed_read_halt_limit = d.failed_read_halt_limit;
    this.temperature_high_setting = d.temperature_high_setting;
    this.temperature_low_setting = d.temperature_low_setting;
    this.humidity_setting = d.humidity_setting;
    this.air_circulation_minutes = d.air_circulation_minutes;
    this.circulation_cycle_minutes = d.circulation_cycle_minutes;
    this.ventilation_cycle_minutes = d.ventilation_cycle_minutes;
    this.stage_limit_minutes = d.stage_limit_minutes;
    this.stage_cooldown_minutes = d.stage_cooldown_minutes;
    this.use_whole_house_fan = d.use_whole_house_fan;
    this.system_disabled = d.system_disabled;
    this.swing_temp_offset = d.swing_temp_offset;
  }
}
export class State {
  temperature: number;
  humidity: number;
  heat_on: boolean;
  ac_on: boolean;
  fan_on: boolean;
  whf_on: boolean;
  status: string;
  public constructor(d: any) {
    this.temperature = d.temperature;
    this.humidity = d.humidity;
    this.heat_on = d.heat_on;
    this.ac_on = d.ac_on;
    this.fan_on = d.fan_on;
    this.whf_on = d.whf_on;
    this.status = d.status;
  }
}
export class RollershadesEntity {
  name: string;
  shade_up?: (boolean)[] | null;
  public constructor(d: any) {
    this.name = d.name;
    this.shade_up = d.shade_up;
  }
}
export class CircuitsEntity {
  id: string;
  ip_address: string;
  name: string;
  relay_id: string;
  rollershutter: boolean;
  location: string;
  zones?: (string | null)[] | null;
  on_modes?: (string | null)[] | null;
  off_modes?: (string | null)[] | null;
  status: Status;
  public constructor(d: any) {
    this.id = d.id;
    this.ip_address = d.ip_address;
    this.name = d.name;
    this.relay_id = d.relay_id;
    this.rollershutter = d.rollershutter;
    this.location = d.location;
    this.zones = d.zones;
    this.on_modes = d.on_modes;
    this.off_modes = d.off_modes;
    this.status = d.status;
  }
}
export class Status {
  relay: Relay;
  temperature: string | number;
  temperature_f: number;
  overtemperature: number;
  temperature_status: string;
  voltage: number;
  public constructor(d: any) {
    this.relay = d.relay;
    this.temperature = d.temperature;
    this.temperature_f = d.temperature_f;
    this.overtemperature = d.overtemperature;
    this.temperature_status = d.temperature_status;
    this.voltage = d.voltage;
  }
}
export class Relay {
  on: boolean;
  power: number;
  energy: number;
  public constructor(d: any) {
    this.on = d.on;
    this.power = d.power;
    this.energy = d.energy;
  }
}
