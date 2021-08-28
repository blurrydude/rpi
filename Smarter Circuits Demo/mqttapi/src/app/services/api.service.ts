import { HttpClient, HttpErrorResponse, HttpHeaders, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
    providedIn:'root'
})
export class ApiService {
    private baseurl: string;
    private options: {
        headers: HttpHeaders
        params: HttpParams
    }

    constructor(private http: HttpClient) {
        this.baseurl = "http://192.168.0.8:8080/";
        this.options = {
            headers: new HttpHeaders(),
            params: new HttpParams()
        }
    }

    public getStates() {
        return this.http.get(this.baseurl+"states", this.options)
            .pipe(
                catchError(err => {
                    return this.handleError(err);
                })
            );
            
    }

    public sendCommand(command) {
        return this.http.get(this.baseurl+"control/"+command, this.options)
            .pipe(
                catchError(err => {
                    return this.handleError(err);
                })
            )
    }

    private handleError(error: HttpErrorResponse) {
        console.error("an error occured: ", error.error);
        return throwError("Bad");
    }
}