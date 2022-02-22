import { IDateRange, IPicture, IPictureInfo, IYearDateRange } from "./Interfaces";

export const PictureInfoConverter : (info: IPictureInfo) => IPictureInfo = (picture: IPictureInfo) => {
    return {...picture, creation_time_date: new Date(picture.creation_time)};
}

export const PictureConverter : (picture: IPicture) => IPicture = (picture: IPicture) => {
    return {...picture, info: PictureInfoConverter(picture.info), rank: 1}
}

export const shortenString : (input: string, maxLength: number) => string = (input: string, maxLength: number) => {
    const totalLength = input.length;

    if (totalLength <= maxLength) {
        return input;
    } else {
        return "..." + input.substring(totalLength - maxLength, totalLength)
    }
}

export const refreshPictureList = (currentList: IPicture[], updatedList: IPicture[]): IPicture[] => {
    const updatedPictureMap = getIndexedPictureMap(updatedList);
    
    return currentList.map((picture) => {
        if(updatedPictureMap.has(picture.hash)){
            let updatedPicture = updatedPictureMap.get(picture.hash) as IPicture;
            let actualRank = picture.rank;
            if(actualRank === undefined){
                actualRank = 1;
            }
            updatedPicture.rank = actualRank + 1;
            
            return updatedPicture;
        } else {
            return picture;
        }
    });  
}

export const getIndexedPictureMap = (pictureList: IPicture[]): Map<string, IPicture> => {
    const result = new Map<string, IPicture>();

    for(let picture of pictureList){
        result.set(picture.hash, picture)
    }

    return result;
}

export const groupDateRangeByYear = (dateRangeList: IDateRange[]): IYearDateRange[] => {
    const result = new Map<number, IDateRange[]>();

    for(let dateRange of dateRangeList){
        const year = dateRange.start.getFullYear();

        if(!result.has(year)){
            result.set(year, []);
        }

        result.get(year)?.push(dateRange);
    }

    const output : IYearDateRange[] = [];

    result.forEach((dateRangeList, year) => {
        const yearTotalPictureCount = dateRangeList.map(
            dateRange => (dateRange.pictureCount)
        ).reduce(
            (a, b) => a + b
        , 0);

        output.push({ year: year, pictureCount: yearTotalPictureCount, dateRangeList: dateRangeList});
    });

    return output;
}

export const getFrenchMonth = (input: Date) : string => {
    const frenchMonth : Map<number, string> = new Map([
        [0, "Janvier"],
        [1, "Février"],
        [2, "Mars"],
        [3, "Avril"],
        [4, "Mai"],
        [5, "Juin"],
        [6, "Juillet"],
        [7, "Août"],
        [8, "Septembre"],
        [9, "Octobre"],
        [10, "Novembre"],
        [11, "Décembre"]
    ]);

    const monthNumber = input.getMonth();

    if(frenchMonth.has(monthNumber)){
        return frenchMonth.get(monthNumber) as string;
    }else{
        throw new Error("Not found");
    }
};

export const buildDateRangeLink : (start: Date, end: Date) => string = (start, end) => {
    return `/pictures/${start.toISOString()}/${end.toISOString()}`;
};