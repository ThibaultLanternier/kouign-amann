import { IPicture, IPictureInfo } from "./App";

export const PictureInfoConverter : (info: IPictureInfo) => IPictureInfo = (picture: IPictureInfo) => {
    return {...picture, creation_time_date: new Date(picture.creation_time)};
}

export const PictureConverter : (picture: IPicture) => IPicture = (picture: IPicture) => {
    return {...picture, info: PictureInfoConverter(picture.info), rank: 1}
}

export const ReduceString : (input: string, maxLength: number) => string = (input: string, maxLength: number) => {
    const totalLength = input.length;

    if (totalLength <= maxLength) {
        return input;
    } else {
        return "..." + input.substring(totalLength - maxLength, totalLength)
    }
}

export const RefreshPictureList = (currentList: IPicture[], updatedList: IPicture[]): IPicture[] => {
    const updatedPictureMap = GetPictureMap(updatedList);
    
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

export const GetPictureMap = (pictureList: IPicture[]): Map<string, IPicture> => {
    const result = new Map<string, IPicture>();

    for(let picture of pictureList){
        result.set(picture.hash, picture)
    }

    return result;
}