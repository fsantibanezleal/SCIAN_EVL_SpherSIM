function [DFC1,DFC2] = SolveCollision_DFC2DFC(DFC1,DFC2)
%% Verify Contours interacting
    nVertexs1 = size(DFC1.contour.XYZ,1);
    nVertexs2 = size(DFC2.contour.XYZ,1);
    % Filling contour position
    % Updating Spherical coordinates    
    % [azimuth,elevation,r] = cart2sph(X,Y,Z)  
    dfcRadialSize1 = DFC1.radialSize;
    dfcRadialSize2 = DFC2.radialSize;
    
    stepAngle1     = (2*pi) /nVertexs1;
    stepAngle2     = (2*pi) /nVertexs2;
    currentAngle1  = 0;
    currentAngle2  = 0;
    
    %% Verify collision between rays
    % Define segments:
    %is of the form [x1 y1 x2 y2] where (x1,y1) is the 
    % start point and (x2,y2) is the end point of a line segment:            
    repCenter1 = repmat(DFC1.center.AER(1:2),nVertexs1,1);
    repCenter2 = repmat(DFC2.center.AER(1:2),nVertexs1,1);    

    segment1 = [repCenter1...
                DFC1.contour.AER(:,[1:2])];
    segment2 = [repCenter2...
                DFC2.contour.AER(:,[1:2])];
    intData  = lineSegmentIntersect(segment1,segment2);

    % Matrix of distance
    dX1   = intData.intMatrixX - repmat(repCenter1(:,1),1,nVertexs1);
    dY1   = intData.intMatrixY - repmat(repCenter1(:,2),1,nVertexs1);
    dD1   = dX1.^2 + dY1.^2;
    [~, idx1] = min(dD1,[],2);
    
    dX2   = intData.intMatrixX - repmat(repCenter2(:,1)',nVertexs2,1);
    dY2   = intData.intMatrixY - repmat(repCenter2(:,2)',nVertexs2,1);
    dD2   = dX2.^2 + dY2.^2;
    [~, idx2] = min(dD2,[],1);
    
    % fix NaN values
    intData.intMatrixX(isnan(intData.intMatrixX)) = 0;
    intData.intMatrixY(isnan(intData.intMatrixY)) = 0;
    
    % Final valid positions---
    vX1 = diag(intData.intMatrixX(1:nVertexs1,idx1));
    vY1 = diag(intData.intMatrixY(1:nVertexs1,idx1));    
    vA1 = diag(intData.intAdjacencyMatrix(1:nVertexs1,idx1));

    vX2 = diag(intData.intMatrixX(idx2,1:nVertexs2));
    vY2 = diag(intData.intMatrixY(idx2,1:nVertexs2));    
    vA2 = diag(intData.intAdjacencyMatrix(idx2,1:nVertexs2));    
    % Updating position for colliding vertexs
    DFC1.contour.AER(:,1:2) = ...
        [vA1.*vX1 vA1.*vY1] + ...
        DFC1.contour.AER(:,1:2) .* repmat((1 - vA1),1,2);
    
    DFC2.contour.AER(:,1:2) = ...
        [vA2.*vX2 vA2.*vY2] + ...
        DFC2.contour.AER(:,1:2) .* repmat((1 - vA2),1,2);
    
%     for indexContour1 = 1:nVertexs1
%         for indexContour2 = 1:nVertexs2        
%             %radiusUpdated1 = dfcRadialSize1;
%             %radiusUpdated2 = dfcRadialSize2;
%             bColliding      = ...
%                 intData.intAdjacencyMatrix(indexContour1,indexContour2);
%             %% Correct vertex positions
%             if bColliding
%                 % DFC1
%                 DFC1.contour.AER(indexContour1,1) = ...
%                     intData.intMatrixX(indexContour1,indexContour2);
%                     %DFC1.center.AER(1) + radiusUpdated1 * cos(currentAngle1);
%                 DFC1.contour.AER(indexContour1,2) = ...
%                     intData.intMatrixY(indexContour1,indexContour2);
%                     %DFC1.center.AER(2) + radiusUpdated1 * sin(currentAngle1);
%                 % DFC1
%                 DFC2.contour.AER(indexContour2,1) = ...
%                     intData.intMatrixX(indexContour1,indexContour2);
%                     %DFC2.center.AER(1) + radiusUpdated2 * cos(currentAngle2);
%                 DFC2.contour.AER(indexContour2,2) = ...
%                     intData.intMatrixY(indexContour1,indexContour2);
%                     %DFC2.center.AER(2) + radiusUpdated2 * sin(currentAngle2);
%             end            
%             % Updating angle 2
%             currentAngle2 = currentAngle2 + stepAngle2;
%         end
%         % Updating angle 1
%         currentAngle1 = currentAngle1 + stepAngle1;
%     end
    
    %% Updating Cartesian coordinates
    % DFC1
    [dummyX,dummyY,dummyZ] = sph2cart(...
                                DFC1.contour.AER(:,1),...
                                DFC1.contour.AER(:,2),...
                                DFC1.contour.AER(:,3));
    DFC1.contour.XYZ    = [dummyX,dummyY,dummyZ]; 
    % DFC2
    [dummyX,dummyY,dummyZ] = sph2cart(...
                                DFC2.contour.AER(:,1),...
                                DFC2.contour.AER(:,2),...
                                DFC2.contour.AER(:,3));
    DFC2.contour.XYZ    = [dummyX,dummyY,dummyZ]; 
end

