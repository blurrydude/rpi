import { OnInit, Component, ElementRef, Input, Output, ViewChild } from '@angular/core';
import { StatusService } from "../../services/status.service";
import { GoogleChartComponent } from 'angular-google-charts';  

@Component({
  selector: 'home',
  templateUrl: './home.component.html'
})
export class HomeComponent implements OnInit {
    @Output() status: object = {};
    @Output() pistatus: object = {};
    @Output() readings: object = {};
    @Output() checkins: object = {};
    @Output() motionsensors: object = {};
    @Output() thsensors: object = {};
    @Output() doors: object = {};
    @Output() rollers: object = {};
    @Output() totalPower: number = 0.0;
    @Output() sysmonlog: any = [];
    @Output() apilog: any = [];
    @Output() mode: any = [];
    @Output() fast: boolean = true;
    @Output() live: boolean = true;
    @Output() local: boolean = true;
    @Output() loghours: number = 2;
    firstLoad: boolean = true;
    logtick: number = 0;
    canvasX: number = 0;
    canvasY: number = 0;
    scale: number = 1.6;

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

    constructor(public httpMessageService: StatusService) { 
      this.load(httpMessageService, true);
    }

    public canvasClick(event: any) {
      console.log("clicked "+(event.clientX-this.canvasX)+" "+(event.clientY-this.canvasY));
      let clickX = event.clientX-this.canvasX;
      let clickY = event.clientY-this.canvasY;
      for(let i = 158; i < this.housepoints.length; i++) {
        let p = this.housepoints[i];
        let c = this.housecircuits[i - 158];
        let l = p[0]*this.scale - 10;
        let r = p[0]*this.scale + 50;
        let t = p[1]*this.scale - 10;
        let b = p[1]*this.scale + 10;
        if(clickX >= l && clickX <= r && clickY >= t && clickY <= b) {
          console.log(c+" clicked!");
        }
      }
    }

    ngOnInit(): void {
      console.log("I inited.");
      let rect = this.myCanvas.nativeElement.getBoundingClientRect();
      this.canvasX = rect.x;
      this.canvasY = rect.y;
      this.context = this.myCanvas.nativeElement.getContext('2d');
      this.context.fillStyle = 'white';
      

      this.context.strokeStyle = '#009900';
      this.context.lineWidth = 2;
      this.context.beginPath();
      this.houselines.forEach(line => {
        let p1 = this.housepoints[line[0]];
        let p2 = this.housepoints[line[1]];
        this.context.moveTo(p1[0]*this.scale,p1[1]*this.scale);
        this.context.lineTo(p2[0]*this.scale,p2[1]*this.scale);
      });
      this.context.stroke();

      this.context.strokeStyle = '#000099';
      this.context.lineWidth = 2;
      this.context.beginPath();
      this.housedoors.forEach(door => {
        let p1 = this.housepoints[door[0]];
        let p2 = this.housepoints[door[1]];
        this.context.moveTo(p1[0]*this.scale,p1[1]*this.scale);
        this.context.lineTo(p2[0]*this.scale,p2[1]*this.scale);
      });
      this.context.stroke();

      let i = 0;
      this.housepoints.forEach(point => {
        let x = point[0];
        let y = point[1];
        this.context.fillRect(x*this.scale,y*this.scale,2,2);
        if (i > 157) {
          let cindex = i - 158;
          //this.context.fillText(cindex+'',x+3,y+3);
          this.context.fillText(this.housecircuits[cindex],x*this.scale+3,y*this.scale+3);
        }
        i++;
      });
      //this.context.fillRect(0, 0, 5, 5);
      
      //this.context.strokeStyle = '#ff0000';
      //this.context.beginPath();
      //this.context.moveTo(153,210);
      //this.context.lineTo(372,210);
      //this.context.stroke();
    }

    public sendThermosettings(room: string, temp_low: number, temp_high: number, humidity: number, circ_min: number, hum_circ_min: number, stage_limit: number, stage_cooldown: number, swing_temp_offset: number, vent_min: number, system_disabled: boolean) {
      this.httpMessageService.sendThermosettings(room,temp_low,temp_high,humidity,circ_min,hum_circ_min, stage_limit, stage_cooldown, swing_temp_offset, vent_min, system_disabled).toPromise().then(smsg => {
        setTimeout(()=>{this.load(this.httpMessageService,false)},500);
      });
    }

    public command(com: string) {
      this.httpMessageService.sendCommand(com).toPromise().then(smsg => {
        setTimeout(()=>{this.load(this.httpMessageService,false)},3000);
      });
    }

    public getLogs() {
      this.httpMessageService.getSysMonLog().toPromise().then(lmsg => {
        this.sysmonlog = lmsg;
      });
    }

    public getApiLogs() {
      this.httpMessageService.getApiLog().toPromise().then(lmsg => {
        this.apilog = lmsg;
      });
    }

    public load(httpMessageService: StatusService, main_loop: boolean) {
      if(main_loop == true) setTimeout(()=>{this.load(httpMessageService, true)},this.fast?5000:15000);
      if(this.live == false && this.firstLoad == false) return;
      if(this.firstLoad == true) this.firstLoad = false;
      this.httpMessageService.getMode().toPromise().then(mmsg => {
        this.mode = mmsg;
      });
      this.httpMessageService.getMotionSensors().toPromise().then(hmsg => {
        this.motionsensors = hmsg;
      });
      if(this.logtick == 0) {
        this.httpMessageService.getTemplog(this.loghours).toPromise().then(hmsg => {
          let data: any = hmsg;
          let chart1data = [];
          let chart4data = [];
          for (const v of data) {
            v[3] = (v[3] == 1 ? 4 : v[3]) + 50;
            v[4] = (v[4] == 1 ? 6 : v[4]) + 50;
            v[5] = (v[5] == 1 ? 8 : v[5]) + 50;
            v[6] = (v[6] == 1 ? 10 : v[6]) + 50;

            v[9] =  (v[9] == 1 ? 12 : v[9]) + 50;
            v[10] = (v[10] == 1 ? 14 : v[10]) + 50;
            v[11] = (v[11] == 1 ? 16 : v[11]) + 50;
            v[12] = (v[12] == 1 ? 18 : v[12]) + 50;

            if(v[1]>0&&v[7]>0) {
              chart1data.push([v[0],v[1],v[7],v[13],v[15],v[3],v[4],v[5],v[9],v[10],v[11],v[12]]);
              chart4data.push([v[0],v[2],v[8],v[14],v[16]]);
            }
          }
          this.chartData.data = chart1data;
          this.chartData.data = Object.assign([], this.chartData.data);
          this.chartData4.data = chart4data;
          this.chartData4.data = Object.assign([], this.chartData4.data);
        });
        this.httpMessageService.getPowerlog(this.loghours).toPromise().then(hmsg => {
          let data: any = hmsg;
          let chart2data = [];
          for (const v of data) {
            chart2data.push(v);
          }
          this.chartData2.data = hmsg;
          this.chartData2.data = Object.assign([], this.chartData2.data);
          let last = this.chartData2.data[this.chartData2.data.length-1];
          this.chartData3.data = [["Power",
            //last[last.length-1]
            {
              v:Math.round((last[last.length-1]/1000)*100),
              f:last[last.length-1]+" W"
            }
          ]];
          this.chartData3.data = Object.assign([], this.chartData3.data);
        });
        this.logtick = this.fast == true ? 12 : 4;
      } else {
        this.logtick--;
      }
      this.httpMessageService.getReadings().toPromise().then(rmsg => {
        this.readings = rmsg;
        this.httpMessageService.getPassiveReadings().toPromise().then(prmsg => {
          this.thsensors = prmsg;
        });
      });
      this.httpMessageService.getDoors().toPromise().then(dmsg => {
        this.doors = dmsg;
      });
      this.httpMessageService.getRollers().toPromise().then(bmsg => {
        this.rollers = bmsg;
      });

      this.httpMessageService.getStatus().toPromise().then(msg => {
        this.status = msg;
        this.totalPower = 0.0;
        for (const [k, v] of Object.entries(this.status)) {
          if(this.chartData2.columnNames.indexOf(k)===-1) {
            this.chartData2.columnNames.push(k);
          }
          this.totalPower += parseFloat(v["power"])
        }
        if(this.chartData2.columnNames.indexOf("Total")===-1) {
          this.chartData2.columnNames.push("Total");
        }
        this.httpMessageService.getPiStatus().toPromise().then(smsg => {
          this.pistatus = smsg;
          for (const [k, v] of Object.entries(this.pistatus)) {
            let s = v["heartbeat"].split('_');
            let d = s[0].split('/');
            let t = s[1];
            let ms = Date.parse(d[2]+"-"+d[0]+"-"+d[1]+"T"+t+".000-04:00");
            let dt = new Date(ms);
            let n = new Date();
            let c = n.getTime() - ms;
            v["class"] = c > 150000 ? "text-danger" : c < 0 ? "text-info" : "text-success";
            v["heartbeat"] = dt;
          }
          this.httpMessageService.getCheckins().toPromise().then(cmsg => {
            this.checkins = cmsg;
            for (const [k, v] of Object.entries(this.checkins)) {
              for (const [sk, sv] of Object.entries(this.status)) {
                if(k != sk) continue;
                if(v.indexOf("NONCOMM") > -1) {
                  sv["checkin"] = "fas fa-tired"
                  continue;
                }
                let s = v.split(', ');
                let d = s[0].split('/');
                let t = s[1];
                let ms = Date.parse(d[2]+"-"+d[0]+"-"+d[1]+"T"+t+".000-04:00");
                let dt = new Date(ms);
                let n = new Date();
                let c = n.getTime() - ms;
                sv["checkin"] = c > 150000 ? "fas fa-dizzy" : c < 0 ? "far fa-question-circle" : "fas fa-signal";
                sv["heartbeat"] = dt;
              }
            }
          });
        });
      });
    }
    
}
