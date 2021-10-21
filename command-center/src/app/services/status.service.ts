import { HttpClient, HttpErrorResponse, HttpHeaders, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
// import { TriageDetailMessage } from '../models/triage-detail-message';
// import { LoanCalculationMessage } from '../models/loan-calculation-message';
// import { LoanMessage } from '../models/loan-message';

@Injectable({
  providedIn: 'root'
})
export class StatusService {
  public auth: string = '';
  public user: string = '';
  private baseurl: string;
  private thing1: string = '240aab02f31767b';
  private thing2: string = 'db4a18d03e3fe8ffb';
  // private byCompanyUrl: string;
  // private triageDetailUrl: string;
  // private loanCalculationUrl: string;
  // private byIdUrl: string;
  // private fileUrl: string;
  private options: {
    headers: HttpHeaders
    params: HttpParams
  };

  constructor(private http: HttpClient) {
    this.baseurl = "https://api.idkline.com/"
    // this.baseurl = "http://localhost:8080/"
    // this.baseurl = environment.loansRequestService;
    // this.byCompanyUrl = environment.loansInformationByCompany;
    // this.byIdUrl = environment.loansInformationById;
    // this.triageDetailUrl = environment.triageDetailByCompany;
    // this.loanCalculationUrl = environment.loanCalculation;
    // this.fileUrl = environment.fileUpload;

    let httpHeaders = new HttpHeaders()
      // httpHeaders.set('client_id', environment.wfsMulesoftClientId);
      // httpHeaders.set('client_secret', environment.wfsMulesoftClientSecret);

    this.options = { headers: httpHeaders, params: new HttpParams() };
  }

  public getStatus() {
    return this.http.get(this.baseurl+"state", this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public getMinerStatus() {
    return this.http.get(this.baseurl+"getminers", this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public getLtcPrice() {
    return this.http.get("https://api.coinbase.com/v2/prices/LTC-USD/sell", this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public getPoolStatus() {
    return this.http.get("https://www.litecoinpool.org/api?api_key="+this.thing1+this.thing2, this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public getApiLog() {
    return this.http.get(this.baseurl+"getapilog", this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public getToken(username: string, passhash: string) {
    return this.http.post(this.baseurl+"gettoken", {"username":username, "passhash":passhash},this.options)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  public sendCommand(command: string) {
    let httpHeaders = new HttpHeaders({
      "user":this.user,
      "auth":this.auth
    });

    let opts = { headers: httpHeaders, params: new HttpParams() };
    console.log(opts)
    return this.http.get(this.baseurl+"webcontrol/"+command, opts)
      .pipe(
        catchError(err => {
          return this.handleError(err);
        })
      );
  }

  private handleError(error: HttpErrorResponse) {
    if (error.status === 0) {
      // A client-side or network error occurred.
      console.error('An error occurred:', error.error);
    } else {
      // The backend returned an unsuccessful response code.
      console.error(
        `Backend returned code ${error.status}, ` +
        `body was:`,error);
    }
    // Return an observable with a user-facing error message.
    return throwError(
      'Something bad happened; please try again later.');
  }
}